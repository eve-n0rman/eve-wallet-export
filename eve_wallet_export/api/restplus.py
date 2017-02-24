import logging
import traceback

from flask_restplus import Api
from eve_wallet_export import settings

log = logging.getLogger(__name__)

api = Api(version='0.1', title='Eve Wallet Export API',
          description='RESTful EVE wallet exporter')


@api.errorhandler
def default_error_handler(e):
    message = 'An unhandled exception occurred.'
    log.exception(message)

    if not settings.FLASK_DEBUG:
        return {'message': message}, 500

