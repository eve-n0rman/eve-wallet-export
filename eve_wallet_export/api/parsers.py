from flask_restplus import reqparse

wallet_arguments = reqparse.RequestParser()
wallet_arguments.add_argument('key', type=int, required=True, help='CCP API Key')
wallet_arguments.add_argument('code', type=str, required=True, help='CCP API vCode')
wallet_arguments.add_argument('type', type=str, required=True, choices=('corp','char'), help='Wallet type (corp or char)')
wallet_arguments.add_argument('division', type=int, default=1000, help='Wallet division (1000 for char or corp division 1, 1001-1006 for other corp divisions)')
wallet_arguments.add_argument('output', type=str, default='csv', choices=('csv','json'))

