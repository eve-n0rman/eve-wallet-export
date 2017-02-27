import logging

from flask_restplus import Resource, fields
from eve_wallet_export.api.business import wallet_to_dataframe, wallet_getter
from eve_wallet_export.api.parsers import wallet_arguments
from eve_wallet_export.api.restplus import api

log = logging.getLogger(__name__)

ns = api.namespace('transactions', description='Wallet Transaction Entries')

# Note these models are only used for documentation at this time, not serialization because
# the dataframe already handles that.
# BUG: need to fix json output to match this
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

@ns.route('/')
class WalletTransaction(Resource):
    @api.expect(wallet_arguments)
    @api.response(200, 'Success - Returns CSV or JSON', transaction_list)
    @api.response(400, 'Validation Error')
    def get(self):
        return wallet_getter(self, "Transactions")