import contextlib

import rmr


def get_range(offset=None, limit=None, limit_default=None, limit_max=None):
    start = 0
    stop = None
    with contextlib.suppress(ValueError):
        start = offset and int(offset) or start
        if start < 0:
            raise rmr.ClientError(
                'Offset must be a positive number',
                code='incorrect_offset',
            )
        limit = limit and int(limit) or limit_default
        if limit is not None:
            if limit <= 0:
                raise rmr.ClientError(
                    'Limit must be a positive number',
                    code='incorrect_limit',
                )
            if limit_max and limit > limit_max:
                raise rmr.ClientError(
                    'Maximum value of limit must be '
                    'less then or equal {}'.format(limit_max),
                    code='max_limit_exceeded',
                )
            stop = start + limit

        return start, stop

    raise rmr.ClientError(
        'Limit and offset must be a numbers if provided',
        code='incorrect_limit_or_offset',
    )
