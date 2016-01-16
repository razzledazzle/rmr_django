import django.test

import rmr

from rmr.utils.range import get_range
from rmr.utils.test import data_provider, DataSet, Parametrized


class RangeTestCase(django.test.TestCase, metaclass=Parametrized):

    @data_provider(
        DataSet(
            offset=None,
            limit=None,
            limit_default=None,
            limit_max=None,
            expected=(0, None),
        ),
        DataSet(
            offset=5,
            limit=10,
            limit_default=None,
            limit_max=None,
            expected=(5, 15),
        ),
        DataSet(
            offset='5',
            limit='10',
            limit_default=None,
            limit_max=None,
            expected=(5, 15),
        ),
        DataSet(
            offset=None,
            limit=10,
            limit_default=None,
            limit_max=None,
            expected=(0, 10),
        ),
        DataSet(
            offset=5,
            limit=None,
            limit_default=None,
            limit_max=None,
            expected=(5, None),
        ),
        DataSet(
            offset=None,
            limit=None,
            limit_default=10,
            limit_max=None,
            expected=(0, 10),
        ),
        DataSet(
            offset=5,
            limit=None,
            limit_default=10,
            limit_max=None,
            expected=(5, 15),
        ),
        DataSet(
            offset=5,
            limit=None,
            limit_default=10,
            limit_max=None,
            expected=(5, 15),
        ),
        DataSet(
            offset=5,
            limit=10,
            limit_default=None,
            limit_max=10,
            expected=(5, 15),
        ),
    )
    def test_get_range(self, offset, limit, limit_default, limit_max, expected):
        self.assertEqual(
            expected,
            get_range(
                offset=offset,
                limit=limit,
                limit_default=limit_default,
                limit_max=limit_max,
            ),
        )

    @data_provider(
        DataSet(
            offset=None,
            limit=-1,
            limit_default=None,
            limit_max=None,
            expected_error_code='incorrect_limit',
        ),
        DataSet(
            offset=-1,
            limit=None,
            limit_default=None,
            limit_max=None,
            expected_error_code='incorrect_offset',
        ),
        DataSet(
            offset='blah',
            limit=None,
            limit_default=None,
            limit_max=None,
            expected_error_code='incorrect_limit_or_offset',
        ),
        DataSet(
            offset=None,
            limit='blah',
            limit_default=None,
            limit_max=None,
            expected_error_code='incorrect_limit_or_offset',
        ),
        DataSet(
            offset=None,
            limit=11,
            limit_default=None,
            limit_max=10,
            expected_error_code='max_limit_exceeded',
        ),
        DataSet(
            offset=None,
            limit=None,
            limit_default=11,
            limit_max=10,
            expected_error_code='max_limit_exceeded',
        ),
    )
    def test_get_range_errors(self, offset, limit, limit_default, limit_max, expected_error_code):
        with self.assertRaises(rmr.ClientError) as error:
            get_range(
                offset=offset,
                limit=limit,
                limit_default=limit_default,
                limit_max=limit_max,
            )
        self.assertEqual(expected_error_code, error.exception.code)
