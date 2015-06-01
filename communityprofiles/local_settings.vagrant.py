import os
DEBUG = True
BETA = True
USE_TZ = True
PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))
BLS_KEYS = ("03ac8d50ab4341e0805cb100cce6a05e",
            "995f4e779f204473aa565256e8afe73e",
            "baf12a8c030b487e94ea96e80f7dd743")



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
    '*',
]

#STATIC_URL="/static/"
#MEDIA_URL="/media/"
PROFILES_API_URL = "http://127.0.0.1:8001" # NOTE no trailing /
BANNER_TEXT = "Community Profiles"

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
		'USER':'vagrant',#'vagrant',
		'NAME':'communityprofiles',#'communityprofiles',
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                    # Set to empty string for localhost. Not used with sqlite3.
        #'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}


PHANTOM_JS_RENDERER = "/path/to/phantomjs/render.js"
PHANTOM_JS_RENDER_DIR = "/tmp/phantom/"

#DEFAULT_GEO_RECORD_ID = 11516

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

LOGO_ICON = 'images/logo1.png'
STATE = 'Rhode Island'
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

GOOGLE_ANALYTICS_UID = 'UA-45520028-1'
CONSTATCONTACT_API_KEY = 'gagydvv3wmguvquvghz4qrg4'
CONSTATCONTACT_SECRET = 'NFH2nXDEaUtKg94NBXyGbWHT'


ADDITIONAL_MIDDLEWARE = ()

# example BOTO AWS storage
"""
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
AWS_ACCESS_KEY_ID = 'YOUR-ACCESS-KEY'
AWS_SECRET_ACCESS_KEY = 'YOUR-SECRET-KEY'
AWS_STORAGE_BUCKET_NAME = 'communityprofiles-dev'
"""

# see http://www.census.gov/developers/tos/key_request.html
CENSUS_API_KEY = '82da0d53d9a57cb23f6e56e92a7c91253eec46da'
STYLE = "css/profiles.css"

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

