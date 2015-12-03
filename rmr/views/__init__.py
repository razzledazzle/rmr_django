from rmr.errors import ClientError

from .json import Json


def anonymous_required(fn):
    def _fn(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            raise ClientError(
                'You can not perform this action while logged in.',
                code='you_can_not_perform_this_action_while_logged_in',
            )
        return fn(self, request, *args, **kwargs)
    return _fn
