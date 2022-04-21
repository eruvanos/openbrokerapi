from os import getenv

from openbrokerapi.helper import version_tuple

MIN_VERSION_STR = "2.13"
MIN_VERSION = version_tuple(MIN_VERSION_STR)

DISABLE_VERSION_CHECK = getenv("DISABLE_VERSION_CHECK", "").lower() == "true"

# Disable the check for space_guid and organization_guid in provision requests
DISABLE_SPACE_ORG_GUID_CHECK = (
    getenv("DISABLE_SPACE_ORG_GUID_CHECK", "").lower() == "true"
)
