import json
import urllib.parse

import django.forms
import django.test

from django.conf.urls import url
from django.core.urlresolvers import reverse
from django.test.utils import override_settings
from django.views.generic import View
from django.utils.decorators import method_decorator

from rmr.utils.test import data_provider, DataSet, Parametrized
from rmr.views.decorators.response import json_response
from rmr.views.decorators.validation import validate_request


class ValidationJson(View):

    class GetValidationForm(django.forms.Form):
        get_required = django.forms.IntegerField()
        get_not_required = django.forms.IntegerField(required=False)

    class PostValidationForm(django.forms.Form):
        post_required = django.forms.IntegerField()
        post_not_required = django.forms.IntegerField(required=False)

    @method_decorator(json_response)
    @method_decorator(validate_request(get=GetValidationForm))
    def get(self, request):
        pass

    @method_decorator(json_response)
    @method_decorator(validate_request(post=PostValidationForm))
    def post(self, request):
        pass

    @method_decorator(json_response)
    @method_decorator(validate_request(
        get=GetValidationForm,
        post=PostValidationForm,
    ))
    def patch(self, request):
        pass

urlpatterns = [
    url(r'validate', ValidationJson.as_view(), name='validate'),
]


@override_settings(ROOT_URLCONF=__name__)
class ValidationTestCase(django.test.TestCase, metaclass=Parametrized):

    def test_validate_request(self):
        client = django.test.Client()
        path = reverse('validate')

        # GET validation
        response = client.get(path, data=dict(
            get_required=123,
            get_not_required=123,
            unknown=123,
        ))
        self.assertEqual(
            200,
            response.status_code,
        )

        # POST validation
        response = client.post(
            path,
            data=json.dumps(dict(
                post_required=123,
                post_not_required=123,
                unknown=123,
            )),
            content_type='application/json',
        )
        self.assertEqual(
            200,
            response.status_code,
        )

        # GET and POST validation
        response = client.patch(
            '{path}?{query}'.format(
                path=path,
                query=urllib.parse.urlencode(dict(get_required=123)),
            ),
            data=json.dumps(dict(post_required=123)),
            content_type='application/json',
        )
        self.assertEqual(
            200,
            response.status_code,
        )

    @data_provider(
        DataSet(
            method='GET',
            query={},
            data={},
            invalid_params={'get_required'},
        ),
        DataSet(
            method='POST',
            query={},
            data={},
            invalid_params={'post_required'},
        ),
        DataSet(
            method='PATCH',
            query={},
            data={},
            invalid_params={'post_required', 'get_required'},
        ),
        DataSet(
            method='PATCH',
            query=dict(get_not_required='wrong_value'),
            data=dict(post_not_required='wrong_value'),
            invalid_params={'post_required', 'get_required', 'get_not_required', 'post_not_required'},
        ),
    )
    def test_validate_request_errors(self, method, query, data, invalid_params):
        client = django.test.Client()
        path = reverse('validate')
        response = client.generic(
            method=method,
            path='{path}?{query}'.format(
                path=path,
                query=urllib.parse.urlencode(query),
            ),
            data=json.dumps(data),
            content_type='application/json',
        )
        self.assertEqual(
            400,
            response.status_code,
        )
        data = json.loads(response.content.decode())
        actual_invalid_params = data.get('error', {}).get('description', {}).keys()
        self.assertSetEqual(invalid_params, set(actual_invalid_params))
