import logging
from flask_restplus import Api
from requests import HTTPError, ConnectionError

log = logging.getLogger(__name__)

api = Api(version='0.1', title='Eve Wallet Export API',
          description='RESTful EVE wallet exporter')

@api.errorhandler(HTTPError)
def requests_http_error_handler(e):
    status_code = e.response.status_code
    log.exception(e)
    return {'message': str(e)}, status_code

@api.errorhandler(ConnectionError)
def requests_http_connection_error_handler(e):
    status_code = e.response.status_code
    log.exception(e)
    return {'message': str(e)}, status_code

@api.errorhandler
def default_error_handler(e):
    message = 'An unhandled exception occurred.'
    log.exception(message)

    if not settings.FLASK_DEBUG:
        return {'message': message}, 500
    else:
        raise e
