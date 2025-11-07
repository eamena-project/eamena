"""
Django settings for eamena project.
"""

import os
import semantic_version
from datetime import datetime, timedelta
from django.utils.translation import gettext_lazy as _

try:
    from arches.settings import *
except ImportError:
    pass
from .settings_paths import *

APP_NAME = 'eamena'
APP_TITLE = 'EAMENA | Endangered Archaeology in the Middle East and North Africa'
APP_VERSION = semantic_version.Version(major=5, minor=1, patch=0)
COPYRIGHT_TEXT = 'All Rights Reserved.'
COPYRIGHT_YEAR = '2025'

WEBPACK_LOADER = {
    "DEFAULT": {
        "STATS_FILE": os.path.join(APP_ROOT, '..', 'webpack/webpack-stats.json'),
    },
}

DATATYPE_LOCATIONS.append('eamena.datatypes')
FUNCTION_LOCATIONS.append('eamena.functions')
ETL_MODULE_LOCATIONS.append('eamena.etl_modules')
SEARCH_COMPONENT_LOCATIONS.append('eamena.search_components')
LOCALE_PATHS.insert(0, os.path.join(APP_ROOT, 'locale'))

FILE_TYPE_CHECKING = "lenient"
FILE_TYPES = [
    "bmp",
    "gif",
    "jpg",
    "jpeg",
    "json",
    "pdf",
    "png",
    "psd",
    "rtf",
    "tif",
    "tiff",
    "xlsx",
    "csv",
    "zip",
]
FILENAME_GENERATOR = "arches.app.utils.storage_filename_generator.generate_filename"
UPLOADED_FILES_DIR = "uploadedfiles"

ROOT_URLCONF = "eamena.urls"
ROOT_HOSTCONF = "eamena.hosts"

DEFAULT_HOST = "eamena"

LOAD_DEFAULT_ONTOLOGY = False
LOAD_PACKAGE_ONTOLOGIES = True

SEARCH_THUMBNAILS = False

INSTALLED_APPS = (
    "webpack_loader",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",
    "django_hosts",
    "arches",
    "arches.app.models",
    "arches.management",
    "guardian",
    "captcha",
    "revproxy",
    "corsheaders",
    "oauth2_provider",
    "django_celery_results",
    "eamena",  # Ensure the project is listed before any other arches applications
)

# Placing this last ensures any templates provided by Arches Applications
# take precedence over core arches templates in arches/app/templates.
INSTALLED_APPS += ("arches.app",)

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
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "arches.app.utils.middleware.SetAnonymousUser",
]

MIDDLEWARE.insert(  # this must resolve to first MIDDLEWARE entry
    0,
    "django_hosts.middleware.HostsRequestMiddleware"
)

MIDDLEWARE.append(  # this must resolve last MIDDLEWARE entry
    "django_hosts.middleware.HostsResponseMiddleware"
)

WSGI_APPLICATION = 'eamena.wsgi.application'
FORCE_SCRIPT_NAME = None # when hosting Arches under a sub path set this value to the sub path eg : "/{sub_path}/"
DEFAULT_RESOURCE_IMPORT_USER = {'username': 'admin', 'userid': 1}
RATE_LIMIT = "5/m"
DATA_UPLOAD_MAX_MEMORY_SIZE = 15728640 # Sets default max upload size to 15MB
HIDE_EMPTY_NODES_IN_REPORT = False # Hide nodes and cards in a report that have no data
BYPASS_UNIQUE_CONSTRAINT_TILE_VALIDATION = False
BYPASS_REQUIRED_VALUE_TILE_VALIDATION = False
DATE_IMPORT_EXPORT_FORMAT = "%Y-%m-%d" # Custom date format for dates imported from and exported to csv
EXPORT_DATA_FIELDS_IN_CARD_ORDER = False

#Identify the usernames and duration (seconds) for which you want to cache the time wheel
CACHE_BY_USER = {
    "default": 3600 * 24, #24hrs
    "anonymous": 3600 * 24 #24hrs
    }

TILE_CACHE_TIMEOUT = 600 #seconds
CLUSTER_DISTANCE_MAX = 5000 #meters
GRAPH_MODEL_CACHE_TIMEOUT = None
OAUTH_CLIENT_ID = ''  #'9JCibwrWQ4hwuGn5fu2u1oRZSs9V6gK8Vu8hpRC4'

ENABLE_CAPTCHA = False
NOCAPTCHA = True

# By setting RESTRICT_MEDIA_ACCESS to True, media file requests will be
# served by Django rather than your web server (e.g. Apache). This allows file requests to be checked against nodegroup permissions.
# However, this will adversely impact performace when serving large files or during periods of high traffic.
RESTRICT_MEDIA_ACCESS = False

CANTALOUPE_DIR = os.path.join(ROOT_DIR, UPLOADED_FILES_DIR)
CANTALOUPE_HTTP_ENDPOINT = "http://localhost:8182/"

ACCESSIBILITY_MODE = False

RENDERERS = [
    {
        "name": "imagereader",
        "title": "Image Reader",
        "description": "Displays most image file types",
        "id": "5e05aa2e-5db0-4922-8938-b4d2b7919733",
        "iconclass": "fa fa-camera",
        "component": "views/components/cards/file-renderers/imagereader",
        "ext": "",
        "type": "image/*",
        "exclude": "tif,tiff,psd",
    },
    {
        "name": "pdfreader",
        "title": "PDF Reader",
        "description": "Displays pdf files",
        "id": "09dec059-1ee8-4fbd-85dd-c0ab0428aa94",
        "iconclass": "fa fa-file",
        "component": "views/components/cards/file-renderers/pdfreader",
        "ext": "pdf",
        "type": "application/pdf",
        "exclude": "tif,tiff,psd",
    },
]

# By setting RESTRICT_MEDIA_ACCESS to True, media file requests outside of Arches will checked against nodegroup permissions.
RESTRICT_MEDIA_ACCESS = False

LANGUAGE_CODE = "en"

# list of languages to display in the language switcher,
# if left empty or with a single entry then the switch won't be displayed
LANGUAGES = [
#   ('de', _('German')),
    ('en', _('English')),
#   ('en-gb', _('British English')),
#   ('es', _('Spanish')),
]

# override this to permenantly display/hide the language switcher
SHOW_LANGUAGE_SWITCH = len(LANGUAGES) > 1

RESOURCE_FORMATTERS['jsonl'] = "eamena.exporters.JsonLWriter"
RESOURCE_FORMATTERS['nt'] = "eamena.exporters.RdfWriter"
RESOURCE_FORMATTERS['n3'] = "eamena.exporters.RdfWriter"
RESOURCE_FORMATTERS['json-ld'] = "eamena.exporters.JsonLdWriter"

from .settings_local import *
from .settings_custom import *
