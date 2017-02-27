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


def wallet_to_dataframe(key, code, char_corp, division=1000, wallet_type="Journal"):
    endpoint = "https://api.eveonline.com/{}/Wallet{}.xml.aspx".format(char_corp, wallet_type)
    request_params = {"keyID": key, "vCode": code, "accountKey": division, "rowCount": 2650}
    wallet_df = pd.DataFrame()
    num_entries = 1
    from_field = "refID" if wallet_type == "Journal" else "transactionID"
    while (num_entries > 0):
        wallet_xml = xml_client.get(endpoint, params=request_params)
        wallet_root = et.fromstring(wallet_xml.content)
        request_df = pd.DataFrame(list(iter_row(wallet_root)))
        num_entries = request_df.shape[0]
        if num_entries > 0:
            wallet_df = wallet_df.append(request_df)
            request_params["fromID"] = request_df[from_field].min()
    wallet_df = wallet_df.apply(lambda x: pd.to_numeric(x, errors='ignore'))
    if wallet_type == "Journal":
        wallet_df["refTypeName"] = wallet_df["refTypeID"].map(ref_type_resolution())
    wallet_df.set_index(from_field, inplace=True)
    return wallet_df
