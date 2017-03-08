import logging
import requests
import pandas as pd
import xml.etree.cElementTree as et
from flask import request, make_response, url_for
from eve_wallet_export.api.parsers import wallet_arguments, wallets_arguments
from werkzeug.exceptions import Forbidden

log = logging.getLogger(__name__)
xml_client = requests.Session()


def xml_api(endpoint, params=None):
    """
    Accesses CCP XML api in a useful way and returns ET root
    """
    xml_response = xml_client.get('https://api.eveonline.com' + endpoint, params=params)
    xml_root = et.fromstring(xml_response.content)
    try:
        xml_response.raise_for_status()
    except requests.HTTPError, e:
        xml_error = xml_root.find('.//error')
        message = "Error code {}: {}".format(xml_error.get('code'), xml_error.text)
        e.args = (message,)
        raise e
    return xml_root


def iter_row(root):
    for row in root.findall('.//row'):
        yield row.attrib


def ref_type_resolution():
    ref_type_root = xml_api("/eve/RefTypes.xml.aspx")
    ref_types = {}
    for ref_type in iter_row(ref_type_root):
        ref_types[int(ref_type['refTypeID'])] = ref_type['refTypeName']
    return ref_types


def wallet_to_dataframe(key, code, char_corp, wallet_type, division=1000, character_id=None):
    endpoint = "/{}/Wallet{}.xml.aspx".format(char_corp, wallet_type)
    request_params = {"keyID": key, "vCode": code, "accountKey": division, "rowCount": 2650}
    if character_id:
        request_params["characterID"] = character_id
    wallet_df = pd.DataFrame()
    num_entries = 1
    from_field = "refID" if wallet_type == "Journal" else "transactionID"
    while (num_entries > 0):
        wallet_root = xml_api(endpoint, params=request_params)
        request_df = pd.DataFrame(list(iter_row(wallet_root)))
        num_entries = request_df.shape[0]
        if num_entries > 0:
            wallet_df = wallet_df.append(request_df)
            request_params["fromID"] = request_df[from_field].min()
    # BUGFIX: Sometimes wallets have no entries!
    if wallet_df.shape[0] > 0:
        wallet_df = wallet_df.apply(lambda x: pd.to_numeric(x, errors='ignore'))
        if wallet_type == "Journal":
            wallet_df["refTypeName"] = wallet_df["refTypeID"].map(ref_type_resolution())
        wallet_df.set_index(from_field, inplace=True)
    return wallet_df


def wallet_entry_getter(self, wallet_type):
    """
    Returns the wallet journal or transactions
    """
    args = wallet_arguments.parse_args(request)
    key = args.get('key')
    code = args.get('code')
    wtype = args.get('type')
    division = args.get('division')
    output = args.get('output')
    character_id = args.get('character_id')
    wallet = wallet_to_dataframe(key, code, wtype, wallet_type, division=division, character_id=character_id)
    if output == 'csv':
        response = make_response(wallet.to_csv(encoding='utf-8'))
        cd = 'attachment; filename=wallet-{}.csv'.format(wallet_type.lower())
        response.headers['Content-Disposition'] = cd
        response.mimetype='text/csv'
        return response
    elif output == 'json':
        response = make_response(wallet.to_json(orient="index"))
        response.mimetype='application/json'
        return response


def get_accessmasks():
    """
    Fetch CCPs current API access masks
    """
    accessmasks_root = xml_api("/api/CallList.xml.aspx")
    accessmasks = {'Corporation': {},
                   'Character': {}}
    for accessmask in accessmasks_root.findall('.//rowset[@name="calls"]/row'):
        accessdict = accessmask.attrib
        accessmasks[accessdict['type']][accessdict['name']] = int(accessdict['accessMask'])
    log.debug(accessmasks)
    return accessmasks


def check_key(key, code):
    """
    Check the provided keys capabilities and return the list of characters/corps it represents
    """
    accessmasks = get_accessmasks()
    required_char_masks = ["WalletTransactions", "WalletJournal", "AccountBalance"]
    required_corp_masks = required_char_masks + ["CorporationSheet"]
    request_endpoint = '/account/APIKeyInfo.xml.aspx'
    request_params = {'keyID': key, 'vCode': code}
    keyinfo_root = xml_api(request_endpoint, params=request_params)
    keyinfo = keyinfo_root.find('.//key').attrib
    keytype = keyinfo['type']
    accessmask = int(keyinfo['accessMask'])
    entities = {}
    entities['type'] = keytype
    entities['entities'] = []
    if keytype == 'Corporation':
        for mask in required_corp_masks:
            if accessmask & accessmasks['Corporation'][mask] == 0:
                log.warn("Missing corp permission: {}".format(mask))
                return False
    if keytype == 'Character':
        for mask in required_char_masks:
            if accessmask & accessmasks['Character'][mask] == 0:
                log.warn("Missing char permission: {}".format(mask))
                return False
    for character_xml in keyinfo_root.findall('.//row'):
        character = character_xml.attrib
        entities['entities'].append(character)
    return entities


def fetch_wallet_balances(key, code, char_corp, character_id):
    endpoint = "/{}/AccountBalance.xml.aspx".format(char_corp)
    balance_root = xml_api(endpoint, params={'keyID': key, 'vCode': code, 'characterID': character_id})
    balances = {}
    for division in balance_root.findall('.//rowset[@name="accounts"]/row'):
        balances[int(division.get('accountKey'))] = float(division.get('balance'))
    log.debug(balances)
    return balances


def fetch_corp_wallet_divisions(key, code):
    corp_sheet_root = xml_api('/corp/CorporationSheet.xml.aspx', params={'keyID': key, 'vCode': code})
    divisions = {}
    for division in corp_sheet_root.findall('.//rowset[@name="walletDivisions"]/row'):
        division_id = int(division.get('accountKey'))
        # BUGFIX: some DUST 514 nonsense that's undocumented in the API
        if division_id == 10000:
            continue
        divisions[division_id] = division.get('description')
    log.debug(divisions)
    return divisions


def fetch_wallets(key, code, entities):
    """
    Given a wallet type, return either a dict of characters or
    corp divisions, balances, and transaction/journal URIs
    """
    wallets = []
    for wallet in entities['entities']:
        wallet['divisions'] = []
        if entities['type'] in ['Character', 'Account']:
            wallet['type'] = 'char'
            division_names = {1000: wallet['characterName']}
        else:
            wallet['type'] = 'corp'
            division_names = fetch_corp_wallet_divisions(key, code)
        division_balances = fetch_wallet_balances(key, code, wallet['type'], wallet['characterID'])
        for division_id, division_name in division_names.iteritems():
            uri_params = {
                'key': key,
                'code': code,
                'type': wallet['type'],
                'division': division_id,
                'character_id': wallet['characterID']
            }
            division = {
                'id': division_id,
                'name': division_name,
                'journal_uri': url_for('api.wallet_journal', **uri_params),
                'transactions_uri': url_for('api.wallet_transactions', **uri_params),
                'balance': division_balances[division_id]
            }
            wallet['divisions'].append(division)       
        wallets.append(wallet)
    log.debug(wallets)
    return {'wallets': wallets}


def wallet_getter(self):
    """
    Returns the list of wallets accesible with this key"""
    args = wallets_arguments.parse_args(request)
    key = args.get('key')
    code = args.get('code')
    entities = check_key(key, code)
    if entities:
        return fetch_wallets(key, code, entities)
    else:
        raise Forbidden('Key does not have appropriate permissions')


