import django.test

from django.conf.urls import url
from django.core.urlresolvers import reverse
from django.test.utils import override_settings
from django.views.generic import View
from django.utils.decorators import method_decorator

import rmr

from rmr.utils.test import data_provider, DataSet, Parametrized
from rmr.views.decorators.response import json_response


class JsonWithWarning(View):

    @method_decorator(json_response)
    def get(self, request):
        raise rmr.ClientError('WARNING_TEST_CASE', code='warning_test_case')


class JsonWithError(View):

    @method_decorator(json_response)
    def get(self, request):
        raise rmr.ServerError('ERROR_TEST_CASE', code='error_test_case')


class JsonWithoutError(View):

    @method_decorator(json_response)
    def get(self, request):
        pass

urlpatterns = [
    url(r'warning', JsonWithWarning.as_view(), name='warning'),
    url(r'error', JsonWithError.as_view(), name='error'),
    url(r'ok', JsonWithoutError.as_view(), name='ok'),
]


@override_settings(ROOT_URLCONF=__name__)
class ResponseTestCase(django.test.TestCase, metaclass=Parametrized):

    @data_provider(
        DataSet('warning', rmr.ClientError.http_code),
        DataSet('error', rmr.ServerError.http_code),
        DataSet('ok', 200),
    )
    def test_status_code(self, url_name, expected_status_code):
        client = django.test.Client()
        response = client.get(reverse(url_name))
        self.assertEqual(expected_status_code, response.status_code)
