import os, inspect

try:
    from arches.settings import build_templates_config, build_staticfiles_dirs
except ImportError:
    pass

APP_ROOT = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

TEMPLATES = build_templates_config(
    debug=False,
    app_root=APP_ROOT,
    additional_directories=[os.path.join(APP_ROOT, 'eamena', 'templates')]
)

SYSTEM_SETTINGS_LOCAL_PATH = os.path.join(APP_ROOT, 'system_settings', 'System_Settings.json')

# URL that handles the media served from MEDIA_ROOT, used for managing stored files.
# It must end in a slash if set to a non-empty value.
MEDIA_URL = '/files/'

# Absolute filesystem path to the directory that will hold user-uploaded files.
MEDIA_ROOT =  '/opt/arches/media'

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = '/opt/arches/static'

RESOURCE_IMPORT_LOG = os.path.join(APP_ROOT, 'logs', 'resource_import.log')

STATICFILES_DIRS = build_staticfiles_dirs(app_root=APP_ROOT)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console': {
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        },
    },
    'handlers': {
        'file': {
            'level': 'WARNING',  # DEBUG, INFO, WARNING, ERROR
            'class': 'logging.FileHandler',
            'filename': os.path.join(APP_ROOT, 'arches.log'),
            'formatter': 'console'
        },
        'console': {
            'level': 'WARNING',
            'class': 'logging.StreamHandler',
            'formatter': 'console'
        }
    },
    'loggers': {
        'arches': {
            'handlers': ['file', 'console'],
            'level': 'WARNING',
            'propagate': True
        }
    }
}
