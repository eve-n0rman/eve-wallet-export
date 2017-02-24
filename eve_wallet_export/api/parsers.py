from flask_restplus import reqparse

journal_arguments = reqparse.RequestParser()
journal_arguments.add_argument('key', type=int, required=True, help='CCP API Key')
journal_arguments.add_argument('code', type=str, required=True, help='CCP API vCode')
journal_arguments.add_argument('type', type=str, required=True, choices=('corp','char'), help='Wallet type (corp or char)')
journal_arguments.add_argument('division', type=int, default=1000, help='Wallet division (1000 for char or corp division 1, 1001-1006 for other corp divisions)')
journal_arguments.add_argument('output', type=str, default='csv', choices=('csv','json'))

