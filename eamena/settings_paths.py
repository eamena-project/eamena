"""
settings_paths.py - Path settings for EAMENA v4

EAMENA v4 is based on Arches 7.3
https://github.com/archesproject/arches

This file is for settings that dictate where the local paths of
various things are on the system. Every version of EAMENA v4 *should*
use the same version of this file, but does not need to. It is
a good idea to keep these paths consistent between versions, however
they may be changed if necessary, for example, when running an
instance on Redhat rather than Ubuntu many system paths will be
different, as will running a development server as opposed to
production.

"""

import os, inspect, arches

try:
    from arches.settings import *
except ImportError:
    pass

APP_ROOT = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
STATICFILES_DIRS =  (
    os.path.join(APP_ROOT, 'media', 'build'),
    os.path.join(APP_ROOT, 'media'),
) + STATICFILES_DIRS

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(APP_ROOT, "staticfiles")

TEMPLATES[0]['DIRS'].append(os.path.join(APP_ROOT, 'functions', 'templates'))
TEMPLATES[0]['DIRS'].append(os.path.join(APP_ROOT, 'widgets', 'templates'))
TEMPLATES[0]['DIRS'].insert(0, os.path.join(APP_ROOT, 'templates'))

LOCALE_PATHS.append(os.path.join(APP_ROOT, 'locale'))

# Absolute filesystem path to the directory that will hold user-uploaded files.
MEDIA_ROOT =  os.path.join(APP_ROOT)
STATIC_ROOT = '/opt/arches/media'

WEBPACK_LOADER = {
    "DEFAULT": {
        "STATS_FILE": os.path.join(APP_ROOT, 'webpack/webpack-stats.json'),
    },
}

SYSTEM_SETTINGS_LOCAL_PATH = os.path.join(APP_ROOT, 'system_settings', 'System_Settings.json')
RESOURCE_IMPORT_LOG = os.path.join(APP_ROOT, 'logs', 'resource_import.log')

BULK_UPLOAD_DIR = '/opt/arches/bulk_uploads'
BULK_UPLOAD_TEMPLATE_DIR = '/opt/arches/bus_templates'
