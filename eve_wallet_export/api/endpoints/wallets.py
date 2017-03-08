from flask_restplus import Resource, fields, marshal_with
from eve_wallet_export.api.business import wallet_getter, wallet_entry_getter
from eve_wallet_export.api.parsers import wallets_arguments, wallet_arguments
from eve_wallet_export.api.restplus import api
from eve_wallet_export.api.serializations import wallets, journal_list, transaction_list

ns = api.namespace('wallet', description='Wallets available through API key', path='/wallet')


@ns.route('/')
class Wallet(Resource):
    @api.expect(wallets_arguments)
    @marshal_with(wallets)
    @api.response(200, 'Success - Returns JSON listing available wallets, divisions and balances', wallets)
    @api.response(400, 'Validation Error')
    @api.response(403, 'Insufficient permissions on API Key')
    def get(self):
        return wallet_getter(self)


@ns.route('/journal')
class Journal(Resource):
    @api.expect(wallet_arguments)
    @api.response(200, 'Success - Returns CSV or JSON of wallet journal', journal_list)
    @api.response(400, 'Validation Error')
    def get(self):
        return wallet_entry_getter(self, "Journal")


@ns.route('/transactions')
class Transactions(Resource):
    @api.expect(wallet_arguments)
    @api.response(200, 'Success - Returns CSV or JSON of wallet transactions', transaction_list)
    @api.response(400, 'Validation Error')
    def get(self):
        return wallet_entry_getter(self, "Transactions")