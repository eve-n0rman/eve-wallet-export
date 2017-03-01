import logging.config
import os

from flask import Flask, Blueprint
from eve_wallet_export import settings
from eve_wallet_export.api.endpoints.journal import ns as wallet_journal_namespace
from eve_wallet_export.api.endpoints.transactions import ns as wallet_transactions_namespace
from eve_wallet_export.api.restplus import api

app = Flask(__name__)
logging.config.fileConfig('logging.conf')
log = logging.getLogger(__name__)


def configure_app(flask_app):
    flask_app.config.from_object('eve_wallet_export.settings')
    if 'EVE_WALLET_EXPORT_DEV_SETTINGS' in os.environ:
        flask_app.config.from_envvar('EVE_WALLET_EXPORT_DEV_SETTINGS')


def initialize_app(flask_app):
    configure_app(flask_app)

    blueprint = Blueprint('api', __name__, url_prefix='/api')
    api.init_app(blueprint)
    api.add_namespace(wallet_journal_namespace)
    api.add_namespace(wallet_transactions_namespace)
    flask_app.register_blueprint(blueprint)


def main():
    initialize_app(app)
    #log.info('>>>>> Starting development server at http://{}/api/ <<<<<'.format(app.config['SERVER_NAME']))
    app.run()

if __name__ == "__main__":
    main()
else:
    initialize_app(app)

