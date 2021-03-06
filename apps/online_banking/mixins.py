from django.core.exceptions import ValidationError
from rest_framework import exceptions as rest_exceptions

from .utils import get_error_message


class ServiceExceptionHandlerMixin:
    """Mixin that transforms django and python exceptions
    into rest_framework ones.
    We use it for the services in the APIs -
    without the mixin, they return 500 status code which is not desired."""

    excepted_exceptions = {
        # Python errors here
        ValueError: rest_exceptions.ValidationError,
        # Django errors here
        ValidationError: rest_exceptions.ValidationError,
        PermissionError: rest_exceptions.PermissionDenied,
    }

    def handle_exception(self, exc):
        print('handle_exception was called')
        if isinstance(exc, tuple(self.excepted_exceptions.keys())):
            drf_exception_class = self.excepted_exceptions[exc.__class__]
            drf_exception = drf_exception_class(get_error_message(exc))

            return super().handle_exception(drf_exception)
        return super().handle_exception(exc)
