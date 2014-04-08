import os
from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS as TCP
from profiles.utils import ProfilesHuey
from census.tools.geography import get_sum_lev_names

DEBUG = False
TEMPLATE_DEBUG = DEBUG
BETA = False

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'communityprofiles',                      # Or path to database file if using sqlite3.
        'USER': 'communityprofiles',                      # Not used with sqlite3.
        'PASSWORD': 'communityprofiles',                  # Not used with sqlite3.
        'HOST': '127.0.0.1',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}


PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/New_York'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_PATH, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = "/media/"

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(PROJECT_PATH, 'static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)
# Make this unique, and don't share it with anybody.
SECRET_KEY = 'mmknxf3c&_o7t8xhq-sh(qi+yvpe2mb-q^tus-&+tu^u@%ip&-'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'django.middleware.common.CommonMiddleware',
    'profiles.middleware.api.XsSharing',
    'django.middleware.cache.FetchFromCacheMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(os.path.dirname(__file__), 'templates'),
)


INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'radmin',
    'django.contrib.admin',
    'django.contrib.humanize',
    'django.contrib.gis',
    'django.contrib.staticfiles',
    'django.contrib.flatpages',
    'django.contrib.markup',
    'adminsortable',
    'haystack',
    'census',
    'profiles',
    'maps',
    'floppyforms',
    'registration',
    'tastypie',
    'sorl.thumbnail',
    'data_displays',
    #'says',
    'compressor',
    'huey.djhuey',
    'south',
    'lilbox',
)

TEMPLATE_CONTEXT_PROCESSORS = TCP + (
    'django.core.context_processors.request',
    'profiles.utils.context_processor',
)

# Allowed domains to access api
XS_SHARING_ALLOWED_ORIGINS = "*"

#---------------CURRENTLY NOT IN USE ----------------
AUTHENTICATION_BACKENDS = (
    "account.emailauth.EmailBackend",
    "django.contrib.auth.backends.ModelBackend",
)
ACCOUNT_ACTIVATION_DAYS = 7
#-------------------------------------------------

SOUTH_TESTS_MIGRATE = False

#---- SEARCH ENGINE Settings
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': os.path.join(os.path.dirname(__file__), 'whoosh_index'),
    },
}


# the Title in the Header
BANNER_TEXT = "Rhode Island Community Profiles"

# Profiles API URL
PROFILES_API_URL = "http://127.0.0.1:8080" # NOTE no trailing /

# Goggle Analytics UID
GOOGLE_ANALYTICS_UID = 'YOUR_GOOGLE_ANALYTICS_INFO'

# Where to store uploaded shapefiles
SHAPE_FILE_STORAGE_PATH = '/tmp/shapefiles'

# The name of the state we are working with
STATE = 'Rhode Island'

# Summary levels used by app
SUMMARY_LEVELS = (
    '040',
    '050',
    '060',
    '140',
    '150',
)

# The landing page Geography id
DEFAULT_GEO_RECORD_ID= 1


# Census Dataset used by app
CENSUS_DATASETS = (
    '2000',
    '2010',
    'acs2010',
)

# API key for census data.
# See http://www.census.gov/developers/tos/key_request.html
CENSUS_API_KEY = ''

# The Redis COnnection used by the task queue
HUEY_SETTINGS = {
    'name':'profiles-queue',
    'connection':{'host': 'localhost', 'port': 6379}
}


# allow for a local override
try:
    from local_settings import *
    INSTALLED_APPS += ADDITIONAL_APPS
    MIDDLEWARE_CLASSES += ADDITIONAL_MIDDLEWARE
    try:
        HUEY_SETTINGS = HUEY_SETTINGS
    except Exception as e:
        print e
except ImportError:
    print 'ImportError loading local_settings'

HUEY = ProfilesHuey(HUEY_SETTINGS.get('name'), **HUEY_SETTINGS.get('connection'))

DEFAULT_GEO_LEVELS = get_sum_lev_names(SUMMARY_LEVELS)

