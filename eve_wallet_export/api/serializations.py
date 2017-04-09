from flask_restplus import fields
from eve_wallet_export.api.restplus import api

division = api.model('Wallet Division', {
        'id': fields.Integer(description='Wallet division ID'),
        'name': fields.String(description='Wallet division name'),
        'balance': fields.Fixed(decimal=2, description=' Wallet division balance'),
        'journal_uri': fields.String(description='API URI for wallet journal'),
        'transactions_uri': fields.String(description='API URI for wallet transactions')
        })

wallet = api.model('Wallet info', {
        'type': fields.String(description='What type of wallet (corp or char)'),
        'characterID': fields.Integer(description='character ID'),
        'characterName': fields.String(description='character name'),
        'corporationID': fields.Integer(description='corporation ID'),
        'corporationName': fields.String(description='corporation name'),
        'divisions': fields.List(fields.Nested(division))
        })

wallets = api.model('Wallets accessible with this API',{
        'types': fields.String(description='What types of wallets are returned by this key (Corporation or Character)'),
        'wallets': fields.List(fields.Nested(wallet))
        })

# Note these models are only used for documentation at this time, not serialization because
# the dataframe already handles that.
# BUG: need to fix json output to match this.  Maybe DO use this for serialization
# TODO: figure out how to add a representation of the CSV data in the swagger UI
transaction_entry = api.model('Wallet transaction entry',{
        'transactionID': fields.Integer(description='Unique tranaction ID.'),
        'transactionDateTime': fields.Date(description='Date and time of transaction.'),
        'quantity': fields.Integer(description='Number of items bought or sold.'),
        'typeName': fields.String(description='Name of item bought or sold.'),
        'typeID': fields.Integer(description='Type ID of item bought or sold.'),
        'price': fields.Fixed(decimal=2, description='Amount paid per unit.'),
        'clientID': fields.Integer(description='Counterparty character or corporation ID.'),
        'clientName': fields.String(description='Counterparty name.'),
        'characterID': fields.Integer(description='Character ID of character which represented corporation in transaction.'),
        'characterName': fields.String(description='Character name of character which represented corporation in transaction.'),
        'stationID': fields.Integer(description='Station ID in which transaction took place.'),
        'stationName': fields.String(description='Name of station in which transaction took place.'),
        'transactionType': fields.String(description='Either "buy" or "sell" as appropriate.'),
        'transactionFor': fields.String(description='Either "personal" or "corporate" as appropriate.'),
        'journalTransactionID': fields.Integer(description='Corresponding wallet journal refID.'),
        'clientTypeID': fields.Integer(description='Type ID of the counterparty.')
    })

transaction_list = api.model('Wallet transaction entries', {
    'transaction entries': fields.List(fields.Nested(transaction_entry))
    })

journal_entry = api.model('Wallet journal entry',{
        'refID': fields.Integer(description='Unique journal reference ID.'),
        'date': fields.Date(description='Date and time of transaction.'),
        'refTypeID': fields.Integer(description='Transaction type ID (resolved in refTypeName)'),
        'refTypeName': fields.String(description='refTypeID resolved per https://api.eveonline.com/eve/RefTypes.xml.aspx'),
        'ownerName1 ': fields.String(description='Name of first party in transaction.'),
        'ownerID1': fields.Integer(description='Character or corporation ID of first party.'),
        'ownerName2': fields.String(description='Name of second party in transaction.'),
        'ownerID2': fields.Integer(description='Character or corporation ID of second party.'),
        'argName1': fields.String(description='Ref type dependent argument name.'),
        'argID1': fields.String(description='Ref type dependent argument value.'),
        'amount': fields.Fixed(decimals=2, description='Transaction amount. Positive when value transferred to the first owner. Negative otherwise.'),
        'balance': fields.Fixed(decimals=2, description='Wallet balance after transaction occurred.'),
        'reason': fields.String(description='Ref type dependent reason.'),
        'taxReceiverID': fields.Integer(description='For tax related transactions, gives the corporation ID of the entity receiving the tax.'),
        'taxAmount': fields.Fixed(decimal=2, description='Tax amount received for tax related transactions.')
    })

journal_list = api.model('Wallet journal entries', {
    'journal entries': fields.List(fields.Nested(journal_entry))
    })