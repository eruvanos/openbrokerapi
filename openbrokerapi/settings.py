from os import getenv

from openbrokerapi.helper import version_tuple

MIN_VERSION_STR = "2.13"
MIN_VERSION = version_tuple(MIN_VERSION_STR)

DISABLE_VERSION_CHECK = getenv('DISABLE_VERSION_CHECK', '').lower() == 'true'
