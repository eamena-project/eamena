"""
settings.py - General settings for EAMENA v4

EAMENA v4 is based on Arches 7.3
https://github.com/archesproject/arches

This file is for settings that customise EAMENA in general, and should
not contain any secret values such as passwords, or paths in the
local filesystem. Every installation of the EAMENA database should
have the same version of this file.

Paths should be in settings_paths.py
Secrets and instance-specific settings should be in settings_local.py

"""

# useful for internationalization/localization
from django.utils.translation import gettext_lazy as _

try:
    from .package_settings import *
except ImportError:
    try:
        from package_settings import *
    except ImportError as e:
        pass

try:
    from arches.settings import *
except ImportError:
    pass

try:
    from .settings_local import *
except ImportError as e:
    try:
        from settings_local import *
    except ImportError as e:
        pass

APP_NAME = 'eamena'

DATATYPE_LOCATIONS.append('eamena.datatypes')
FUNCTION_LOCATIONS.append('eamena.functions')
ETL_MODULE_LOCATIONS.append('eamena.etl_modules')
SEARCH_COMPONENT_LOCATIONS.append('eamena.search_components')

FILE_TYPES = ["bmp", "gif", "jpg", "jpeg", "pdf", "png", "psd", "rtf", "tif", "tiff", "xlsx", "csv", "zip"]

ROOT_URLCONF = 'eamena.urls'

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "arches.app.utils.middleware.ModifyAuthorizationHeader",
    "oauth2_provider.middleware.OAuth2TokenMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "arches.app.utils.middleware.SetAnonymousUser",
]

WSGI_APPLICATION = 'eamena.wsgi.application'

# URL that handles the media served from MEDIA_ROOT, used for managing stored files.
# It must end in a slash if set to a non-empty value.
# MEDIA_URL = '/files/'
MEDIA_URL = '/uploadedfiles/'

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# when hosting Arches under a sub path set this value to the sub path eg : "/{sub_path}/"
FORCE_SCRIPT_NAME = None

# Unique session cookie ensures that logins are treated separately for each app
SESSION_COOKIE_NAME = 'eamena'

APP_TITLE = 'EAMENA v4'
COPYRIGHT_TEXT = 'All Rights Reserved.'
COPYRIGHT_YEAR = '2023'

ACCESSIBILITY_MODE = False

# By setting RESTRICT_MEDIA_ACCESS to True, media file requests outside of Arches will checked against nodegroup permissions.
RESTRICT_MEDIA_ACCESS = False

# default language of the application
# language code needs to be all lower case with the form:
# {langcode}-{regioncode} eg: en, en-gb ....
# a list of language codes can be found here http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = "en"

# list of languages to display in the language switcher,
# if left empty or with a single entry then the switch won't be displayed
# language codes need to be all lower case with the form:
# {langcode}-{regioncode} eg: en, en-gb ....
# a list of language codes can be found here http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGES = [
    ('en', _('English')),
    # ('fr', _('French')),
    ('ar', _('Arabic')),
]

# override this to permenantly display/hide the language switcher
SHOW_LANGUAGE_SWITCH = len(LANGUAGES) > 1

INSTALLED_APPS = [
    "webpack_loader",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",
    "arches",
    "arches.app.models",
    "arches.management",
    "guardian",
    "captcha",
    "revproxy",
    "corsheaders",
    "oauth2_provider",
    "django_celery_results",
    "eamena",
    "compressor",
]

RESOURCE_FORMATTERS['jsonl'] = "eamena.exporters.JsonLWriter"
RESOURCE_FORMATTERS['nt'] = "eamena.exporters.RdfWriter"
RESOURCE_FORMATTERS['n3'] = "eamena.exporters.RdfWriter"
RESOURCE_FORMATTERS['json-ld'] = "eamena.exporters.JsonLdWriter"

# returns an output that can be read by NODEJS
if __name__ == "__main__":
    print(
        json.dumps({
            'ARCHES_NAMESPACE_FOR_DATA_EXPORT': ARCHES_NAMESPACE_FOR_DATA_EXPORT,
            'STATIC_URL': STATIC_URL,
            'ROOT_DIR': ROOT_DIR,
            'APP_ROOT': APP_ROOT,
            'WEBPACK_DEVELOPMENT_SERVER_PORT': WEBPACK_DEVELOPMENT_SERVER_PORT,
        })
    )
    sys.stdout.flush()

