#!/usr/bin/env python3

import logging
import sentry_sdk
from io import BytesIO
from typing import Dict, Optional

from flask import Flask, abort, redirect, request
from flask_cors import CORS
from PIL import ImageFile, JpegImagePlugin
from werkzeug import Response

from its.errors import ITSClientError, NotFoundError
from its.loader import loader
from its.normalize import NormalizationError, normalize
from its.optimize import optimize
from its.pipeline import process_transforms
from its.settings import MIME_TYPES

from .settings import CORS_ORIGINS, NAMESPACES, SENTRY_DSN
from .util import get_redirect_location

from sentry_sdk.integrations.flask import FlaskIntegration

# https://stackoverflow.com/questions/12984426/python-pil-ioerror-image-file-truncated-with-big-images
ImageFile.LOAD_TRUNCATED_IMAGES = True

# workaround for https://github.com/python-pillow/Pillow/issues/1138
# without this hack, pillow misidenfifies some jpeg files as "mpo" files
JpegImagePlugin._getmp = lambda x: None  # noqa

APP = Flask(__name__)

# enable cors headers on all routes
# https://flask-cors.corydolphin.com/en/latest/api.html#extension
CORS(APP, origins=CORS_ORIGINS)

LOGGER = logging.getLogger(__name__)

if SENTRY_DSN:
    sentry_sdk.init(
        SENTRY_DSN,
        integrations=[FlaskIntegration()]
    )


def _normalize_query(query: Dict[str, str]) -> Dict[str, str]:
    fit_synonyms = {"crop", "focalcrop"}
    if len((fit_synonyms | {"fit"}) & set(query.keys())) > 1:
        raise ITSClientError("use only one of these synonyms: fit, crop, focalcrop")

    for fit_snynonym in fit_synonyms:
        if fit_snynonym in query:
            query["fit"] = query[fit_snynonym]
            del query[fit_snynonym]

    return query


def process_request(namespace: str, query: Dict[str, str], filename: str) -> Response:
    query = _normalize_query(query)

    if namespace not in NAMESPACES:
        abort(
            400, "{namespace} is not a configured namespace".format(namespace=namespace)
        )

    namespace_config = NAMESPACES[namespace]
    if namespace_config.get("redirect"):
        location = get_redirect_location(namespace, query, filename)
        return redirect(location=location, code=301)

    try:
        image = loader(namespace, filename)
    except NotFoundError:
        abort(404)

    # PIL doesn't support SVG and ITS doesn't change them in any way,
    # so loader returns a ByesIO object so the images will still be returned to the browser.
    # This BytesIO object is returned from each loader class's get_fileobj() function.
    if isinstance(image, BytesIO):
        output = image
        mime_type = MIME_TYPES["SVG"]
    else:
        try:
            image = normalize(image)
        except NormalizationError as err:
            LOGGER.warning("failed to normalize %s/%s: %s", namespace, filename, err)
        image.info["filename"] = filename
        result = process_transforms(image, query)

        # image conversion and compression
        # cache result
        result = optimize(result, query)

        if result.format is None:
            result.format = image.format

        mime_type = MIME_TYPES[result.format.upper()]

        output = BytesIO()

        if result.format.upper() in ("JPEG", "JPG"):
            result.save(
                output, format=result.format.upper(), progressive=True, optimize=True
            )
        else:
            result.save(output, format=result.format.upper())

    # our images are cacheable for one year
    # NOTE this would be the right place to do clever things like:
    # allow developers to deactivate caching locally
    # include validation tokens (etags)
    resp_headers = {"Cache-Control": "max-age=31536000"}

    return Response(
        response=output.getvalue(), headers=resp_headers, mimetype=mime_type
    )


def process_old_request(  # pylint: disable=too-many-arguments
    transform: str,
    width: Optional[int] = None,
    height: Optional[int] = None,
    ext: Optional[str] = None,
    x_coordinate: Optional[int] = None,
    y_coordinate: Optional[int] = None,
) -> Dict[str, str]:

    query = {}
    query[transform] = "x"

    if width is not None:
        query[transform] = str(width) + query[transform]

    if height is not None:
        query[transform] = query[transform] + str(height)

    if ext is not None:
        query["format"] = ext

    if x_coordinate is not None:
        query[transform] = query[transform] + "x" + str(x_coordinate)

    if y_coordinate is not None:
        query[transform] = query[transform] + "x" + str(y_coordinate)

    return query

@APP.route('/debug-sentry')
def trigger_error():
    division_by_zero = 1 / 0

@APP.route("/<namespace>/<path:filename>", methods=["GET"])
def transform_image(namespace: str, filename: str) -> Response:
    """ New ITS image transform command """
    query = request.args.to_dict()
    result = process_request(namespace, query, filename)
    return result


# Old ITS Support
@APP.route("/<namespace>/<path:filename>.crop.<int:width>x<int:height>.<ext>")
def crop(namespace: str, filename: str, width: int, height: int, ext: str) -> Response:
    query = process_old_request("fit", width, height, ext)
    result = process_request(namespace, query, filename)
    return result


@APP.route(
    "/<namespace>/<path:filename>.focalcrop.<int:width>x<int:height>."
    + "<int(min=0,max=100):x_coordinate>.<int(min=0,max=100):y_coordinate>.<ext>"
)  # pylint: disable=too-many-arguments
def focalcrop(
    namespace: str,
    filename: str,
    width: int,
    height: int,
    x_coordinate: int,
    y_coordinate: int,
    ext: str,
) -> Response:
    query = process_old_request("fit", width, height, ext, x_coordinate, y_coordinate)
    result = process_request(namespace, query, filename)
    return result


@APP.route("/<namespace>/<path:filename>.fit.<int:width>x<int:height>.<ext>")
def fit(namespace: str, filename: str, width: int, height: int, ext: str) -> Response:
    query = process_old_request("fit", width, height, ext)
    result = process_request(namespace, query, filename)
    return result


# resize with pseduo-optional arguments
@APP.route("/<namespace>/<path:filename>.resize.<int:width>x<int:height>.<ext>")
@APP.route("/<namespace>/<path:filename>.resize.x<int:height>.<ext>")
@APP.route("/<namespace>/<path:filename>.resize.<int:width>x.<ext>")
def resize(
    namespace: str,
    filename: str,
    ext: str,
    width: Optional[int] = None,
    height: Optional[int] = None,
) -> Response:
    query = process_old_request("resize", width, height, ext)
    result = process_request(namespace, query, filename)
    return result


# passport overlay resize with pseduo-optional arguments
@APP.route(
    "/<namespace>/<path:filename>.resize.<int:width>x<int:height>.passport.<ext>"
)
@APP.route("/<namespace>/<path:filename>.resize.x<int:height>.passport.<ext>")
@APP.route("/<namespace>/<path:filename>.resize.<int:width>x.passport.<ext>")
def resize_passport(
    namespace: str, filename: str, width: int, height: int, ext: str
) -> Response:
    query = process_old_request("resize", width, height, ext)
    query["overlay"] = "passport"
    result = process_request(namespace, query, filename)
    return result


# passport overlay fit with pseduo-optional arguments
@APP.route("/<namespace>/<path:filename>.fit.<int:width>x<int:height>.passport.<ext>")
@APP.route("/<namespace>/<path:filename>.fit.x<int:height>.passport.<ext>")
@APP.route("/<namespace>/<path:filename>.fit.<int:width>x.passport.<ext>")
def fit_passport(
    namespace: str, filename: str, width: int, height: int, ext: str
) -> Response:
    query = process_old_request("fit", width, height, ext)
    query["overlay"] = "passport"
    result = process_request(namespace, query, filename)
    return result


@APP.errorhandler(ITSClientError)
def handle_transform_error(error: ITSClientError) -> Response:
    return Response(error.message, status=error.status_code)


if __name__ == "__main__":
    APP.run(debug=True)
