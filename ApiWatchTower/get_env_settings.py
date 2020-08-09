import os
from django.core.exceptions import ImproperlyConfigured

def get_env_value(env_variable, default = None):
    try:
      	return os.environ[env_variable]
    except KeyError:
        if default:
            return default
        error_msg = 'Set the {} environment variable'.format(env_variable)
        raise ImproperlyConfigured(error_msg)
