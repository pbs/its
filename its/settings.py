import json
import os

from newrelic.agent import NewRelicContextFormatter


# Set DEBUG = True to enable debugging application.
DEBUG = os.environ.get("ITS_DEBUG", "false").lower() == "true"

# We don't want to enforce type checks in production environments (probably)
ENFORCE_TYPE_CHECKS = (
    os.environ.get("ITS_ENFORCE_TYPE_CHECKS", "false").lower() == "true"
)

MIME_TYPES = {
    "PNG": "image/png",
    "JPEG": "image/jpeg",
    "JPG": "image/jpeg",
    "WEBP": "image/webp",
    "SVG": "image/svg+xml",
}

PNGQUANT_PATH = os.environ.get("ITS_PNGQUANT_PATH", "pngquant")

DEFAULT_JPEG_QUALITY = int(os.environ.get("ITS_DEFAULT_JPEG_QUALITY", "95"))

DEFAULT_NAMESPACES = json.dumps(
    {
        "default": {"loader": "http", "prefixes": [""]},
        "overlay": {"loader": "file_system", "prefixes": ["test/overlay"]},
        "folders": {"loader": "file_system", "prefixes": [""]},
        "tests": {"loader": "file_system", "folders": ["tests/images"]},
        "merlin": {
            "loader": "http",
            "prefixes": ["s3.amazonaws.com", "pbs.merlin.cdn.prod"],
        },
        "station-images": {
            "redirect": True,
            "url": "https://station-service.example.com/station/image-redirects/",
            "query-param": "url",
        },
    }
)

NAMESPACES = json.JSONDecoder().decode(
    s=os.environ.get("ITS_BACKENDS", DEFAULT_NAMESPACES)
)


DEFAULT_OVERLAYS = json.dumps({"passport": "tests/images/logo.png"})

OVERLAYS = json.JSONDecoder().decode(s=os.environ.get("ITS_OVERLAYS", DEFAULT_OVERLAYS))

# the keyword used to recognize focal point args in filenames
FOCUS_KEYWORD = os.environ.get("ITS_FOCUS_KEYWORD", "focus-")

DELIMITERS_RE = os.environ.get("ITS_DELIMITERS_RE", "[x_,]")

SENTRY_DSN = os.environ.get("ITS_SENTRY_DSN")

# set the ITS_CORS_ORIGINS environment variable to a comma-delimited string of domains
# for each domain in that list, ITS will respond to GET and HEAD requests with CORS headers
CORS_ORIGINS = os.environ.get(
    "ITS_CORS_ORIGINS", "www.example.com,another.example.com"
).split(",")

# Logging dictionary to be used for dictConfig
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s] %(levelname)s - %(name)s - %(message)s'
        },
        'newrelic': {
            '()': NewRelicContextFormatter
        },
    },
    'root': {
        'level': 'DEBUG',
        'class': 'logging.StreamHandler',
        'handlers': ['console', 'newrelic'],
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'formatter': 'verbose',
            'class': 'logging.StreamHandler',
        },
        'newrelic': {
            'level': 'DEBUG',
            'formatter': 'newrelic',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'newrelic': {
            'propagate': True,
            'level': 'ERROR',
        },
    }
}
