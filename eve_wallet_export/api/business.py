import requests
import pandas as pd
import xml.etree.cElementTree as et


xml_client = requests.Session()


def iter_row(root):
    for row in root.findall('.//row'):
        yield row.attrib


def ref_type_resolution():
    ref_type_xml = xml_client.get("https://api.eveonline.com/eve/RefTypes.xml.aspx")
    ref_type_root = et.fromstring(ref_type_xml.content)
    print ref_type_xml.content
    ref_types = {}
    for ref_type in iter_row(ref_type_root):
        ref_types[int(ref_type['refTypeID'])] = ref_type['refTypeName']
    print ref_types
    return ref_types


def journal_to_dataframe(key, code, type, division=1000):
    endpoint = "https://api.eveonline.com/{}/WalletJournal.xml.aspx".format(type)
    from_id = None
    request_params = {"keyID": key, "vCode": code, "accountKey": division, "rowCount": 2650}
    wallet_df = pd.DataFrame()
    num_entries = 1
    while (num_entries > 0):
        wallet_xml = xml_client.get("https://api.eveonline.com/char/WalletJournal.xml.aspx", params=request_params)
        wallet_root = et.fromstring(wallet_xml.content)
        request_df = pd.DataFrame(list(iter_row(wallet_root)))
        num_entries = request_df.shape[0]
        if num_entries > 0:
            wallet_df = wallet_df.append(request_df)
            request_params["fromID"] = request_df["refID"].min()
    wallet_df = wallet_df.apply(lambda x: pd.to_numeric(x, errors='ignore'))
    wallet_df["refTypeName"] = wallet_df["refTypeID"].map(ref_type_resolution())
    wallet_df.set_index("refID", inplace=True)
    return wallet_df
