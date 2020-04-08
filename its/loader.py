"""
Script to validate images being submitted for transformation.
"""

import logging

from flask import request
from PIL.Image import DecompressionBombError

from .errors import (
    ConfigError,
    ITSClientError,
    ITSInvalidImageFileError,
    ITSLoaderError,
)
from .loaders import BaseLoader
from .settings import NAMESPACES

LOGGER = logging.getLogger(__name__)


def loader(namespace, filename):

    """
    Loads image using the IMAGE_LOADER specified in settings.
    """
    loader_classes = BaseLoader.__subclasses__()

    if namespace not in NAMESPACES:
        raise ConfigError("No Backend for namespace '%s'." % namespace)

    loader_parameters = NAMESPACES[namespace]
    loader_slug = loader_parameters["loader"]

    matching_loaders = [
        loader for loader in loader_classes if loader.slug == loader_slug
    ]

    if not matching_loaders:
        raise ITSLoaderError("No Image Loader with slug '%s' found." % loader_slug)

    if len(matching_loaders) > 1:
        raise ConfigError("Two or more Image Loaders have slug '%s'." % loader_slug)

    image_loader = matching_loaders[0]

    # handle self-referential http backend use.
    # if we get a request like /my_http_backend/image.example.com/test/image.jpg,
    # we want to serve as if we got `/test/image.jpg`
    path_segments = filename.split("/")
    if image_loader.slug == "http" and path_segments[0] == request.host:
        namespace = path_segments[1]
        filename = "/".join(path_segments[2:])
        return loader(namespace, filename)

    if filename.endswith(".svg"):
        return image_loader.get_fileobj(namespace, filename)

    try:
        image = image_loader.load_image(namespace, filename)
    except OSError as error:
        LOGGER.error(error)
        raise ITSClientError(
            "{ns}/{fn} is not an image file".format(ns=namespace, fn=filename)
        )
    except ITSInvalidImageFileError:
        raise ITSClientError(
            "{ns}/{fn} is not a supported file type".format(ns=namespace, fn=filename)
        )
    except DecompressionBombError:
        raise ITSClientError(
            "{ns}/{fn}  is too large. Please use a smaller one".format(
                ns=namespace, fn=filename
            )
        )

    return image
