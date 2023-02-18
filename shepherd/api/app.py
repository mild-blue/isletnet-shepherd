import os
import logging
import uuid
from time import perf_counter
from aiohttp import web
from aiohttp.web_exceptions import HTTPError
from apistrap.errors import InvalidFieldsError

from .openapi import oapi
from .responses import ErrorResponse
from ..errors.api import ApiClientError, ApiServerError, NameConflictError, StorageInaccessibleError, UnknownJobError, \
    UnknownSheepError


def internal_error_handler(error: Exception):
    """
    Handles internal server errors

    :param error: an exception object
    :return: a Flask response
    """
    logging.exception(error)
    return (ErrorResponse({"message": 'Internal server error ({})'.format(str(error))})), 500


def error_handler(error: ApiServerError):
    """
    Handles errors derived from apistrap ApiServerError

    :param error: an exception object
    :return: a Flask response
    """
    return ErrorResponse({"message": str(error)})


def http_error_handler(error: HTTPError):
    """
    Handles HTTP errors

    :param error: an exception object
    :return: a Flask response
    """
    return (ErrorResponse({"message": error.text})), error.status_code


@web.middleware
async def middleware_log_on_request(request: web.Request, handler: web.RequestHandler):

    async def get_request_arguments(request: web.Request) -> dict:

        def optimize_json_info(json: dict, max_chars_amount=100) -> dict:
            for key in json:
                if isinstance(json[key], str) and len(json[key]) >= max_chars_amount:
                    json[key] = '<HIDDEN BIG TEXT>'
            return json

        return optimize_json_info(await request.json()) if await request.text() else {}

    # before request
    request_id = request.match_info['job_id'] if 'job_id' in request.match_info else uuid.uuid4()
    request_args = await get_request_arguments(request)
    logging.info(f'Request {request_id} started. '
                 f'Method: {request.method} {request.path}. Arguments: {request_args or "-"}.')
    total_time = perf_counter()

    # request
    response = await handler(request)

    # after request
    logging.info(
        f'User {request.remote}: Request {request_id} took {int(total_time * 1000)} ms. '
        f'Method: {request.method} {request.path}. Arguments: {request_args or "-"}.'
        f'Response status code: {response.status}.')

    return response


def create_app(debug=None) -> web.Application:
    """
    Create the AioHTTP app.

    :param debug: If set, determines whether the app should run in debug mode.
                  If not set, the `DEBUG` environment variable is used (with False as default).
    :return: a new application object
    """

    app = web.Application(debug=debug if debug is not None else os.getenv('DEBUG', False),
                          client_max_size=10*1024**3,
                          middlewares=[middleware_log_on_request])

    oapi.add_error_handler(NameConflictError, 409, error_handler)
    oapi.add_error_handler(ApiClientError, 400, error_handler)
    oapi.add_error_handler(UnknownJobError, 404, error_handler)
    oapi.add_error_handler(UnknownSheepError, 404, error_handler)
    oapi.add_error_handler(InvalidFieldsError, 400, error_handler)
    oapi.add_error_handler(StorageInaccessibleError, 503, error_handler)
    oapi.add_error_handler(HTTPError, None, http_error_handler)
    oapi.add_error_handler(ApiServerError, 500, error_handler)
    oapi.add_error_handler(Exception, None, internal_error_handler)

    oapi.init_app(app)

    return app
