import functools
import logging

from django.http import HttpResponse, JsonResponse, HttpRequest

import rmr

logger = logging.getLogger('rmr.request')


def json_response(view):
    @functools.wraps(view)
    def _view(request: HttpRequest, *args, **kwargs):
        try:
            http_code = 200
            result = view(request, *args, **kwargs)
            if isinstance(result, HttpResponse):
                return result
            api_result = dict(
                data=result,
            )
        except rmr.Error as error:
            logger.log(
                error.level,
                '%(code)s: %(message)s',
                dict(message=error.message, code=error.code),
            )

            http_code = error.http_code

            api_result = dict(
                error=dict(
                    code=error.code,
                    description=error.message,
                ),
            )

        logger.debug(
            'request_method: %(request_method)s, '
            'request_path: %(request_path)s, '
            'request_headers: %(request_headers)s, '
            'request_params: %(request_params)s, '
            'request_data: %(request_data)s, '
            'response_code: %(response_code)s, '
            'response_data: %(response_data)s',
            dict(
                request_method=request.method,
                request_path=request.path,
                request_headers=request.META,
                request_params=request.GET,
                request_data=request.POST,
                response_code=http_code,
                response_data=api_result,
            ),
        )

        return JsonResponse(api_result, status=http_code)
    return _view
