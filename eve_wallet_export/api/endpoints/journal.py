import logging

from flask_restplus import Resource, fields
from eve_wallet_export.api.business import wallet_to_dataframe, wallet_getter
from eve_wallet_export.api.parsers import wallet_arguments
from eve_wallet_export.api.restplus import api

log = logging.getLogger(__name__)

ns = api.namespace('journal', description='Wallet Journal Entries')

# Note these models are only used for documentation at this time, not serialization because
# the dataframe already handles that.
# BUG: need to fix json output to match this
# TODO: figure out how to add a representation of the CSV data in the swagger UI
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

@ns.route('/')
class WalletJournal(Resource):
    @api.expect(wallet_arguments)
    @api.response(200, 'Success - Returns CSV or JSON', journal_list)
    @api.response(400, 'Validation Error')
    def get(self):
        return wallet_getter(self, "Journal")