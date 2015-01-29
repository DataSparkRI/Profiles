import os

DEBUG = True
BETA = True

PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))
BLS_KEYS = ('')

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# memcached example
"""
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
	'LOCATION': '127.0.0.1:11211',
    }
}

CACHE_MIDDLEWARE_SECONDS = 3600
"""

#Sentry Example
ALLOWED_HOSTS = [
    '.provplan.org',
]

#STATIC_URL="/static/"
#MEDIA_URL="/media/"
PROFILES_API_URL = "http://127.0.0.1:8080" # NOTE no trailing /
BANNER_TEXT = "Community Profiles"
LOGO_ICON = ""
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
		'USER':'communityprofiles',
		'NAME':'communityprofiles',
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                    # Set to empty string for localhost. Not used with sqlite3.
        #'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}


PHANTOM_JS_RENDERER = "/path/to/phantomjs/render.js"
PHANTOM_JS_RENDER_DIR = "/tmp/phantom/"

ADDITIONAL_APPS = (
    #'rhodeisland',
    #'gunicorn',
    #raven.contrib.django', # sentry logging
)


# The redis connection
HUEY_SETTINGS = {
    'name':'pitts-profiles-queue',
    'connection':{'host': 'localhost', 'port': 6379}
}


STATE = 'Pittsburg'
# the default location of the map
CENTER_MAP = "[41.83, -71.41]";

# Census Summary Levels used by app
SUMMARY_LEVELS = (
    '040',
    '050',
    '060',
    '140',
    '150',
)

GOOGLE_ANALYTICS_UID = ''


ADDITIONAL_MIDDLEWARE = ()

# example BOTO AWS storage
"""
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
AWS_ACCESS_KEY_ID = 'YOUR-ACCESS-KEY'
AWS_SECRET_ACCESS_KEY = 'YOUR-SECRET-KEY'
AWS_STORAGE_BUCKET_NAME = 'communityprofiles-dev'
"""

# see http://www.census.gov/developers/tos/key_request.html
CENSUS_API_KEY = ''

LOGGING = {
    'version':1,
    'disable_existing_loggers': True,
    'formatters': {
        'default': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
    },
    'handlers': {
        'console':{
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'default'
        },
        'logfile':{
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename':'/tmp/profiles.log', # put this somewhere useful.
            'maxBytes': 1024*1024*5, # 5MB
            'backupCount': 2,
            'formatter':'default'
        }
    },
    'loggers': {
        'django':{
            'handlers':['console',],
            'propagate': True,
            'level':'INFO',
        },
        'data_adapters':{
            'handlers':['console',],
            'propagate': True,
            'level':'DEBUG',
        },

        'huey.consumer':{
            'handlers':['console',],
            'propagate': True,
            'level':'DEBUG',
        }
    }

}
