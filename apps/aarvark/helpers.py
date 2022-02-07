# C4018 (checking-settings-debug)

from django.conf import settings


def format_internal_error(error):
    message = str(error)
    code = type(error).__name__
    if settings.DEBUG:
        params = {
            'exception': type(error).__name__,
            'message': str(error),
            'trace': traceback.format_list(traceback.extract_tb(
                error.__traceback__)),
        }
        return {
            'code': code,
            'message': message,
            'params': params,
        }
    return {
        'code': code,
        'message': message,
    }
