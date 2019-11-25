from io import BytesIO

import requests
from PIL import Image

from ..errors import ITSLoaderError, NotFoundError
from ..settings import NAMESPACES
from ..util import validate_image_type
from .base import BaseLoader


class HTTPLoader(BaseLoader):

    slug = "http"
    parameter_name = "prefixes"

    @staticmethod
    def get_fileobj(namespace, filename):
        """
        Given a namespace (or directory name) and a filename,
        returns a file-like or bytes-like object.
        """
        prefixes = set(
            filename.rsplit("/", 1)[0].split("/")
        )  # everything before the final slash
        params = NAMESPACES[namespace][HTTPLoader.parameter_name]
        intersect = set(params).intersection(prefixes)

        if not intersect:
            raise NotFoundError("Namespace {} is not configured.".format(namespace))

        if filename.startswith("http"):
            url = filename
        else:
            url = "https://{}".format(filename)
        response = requests.get(url)

        if response.status_code in [403, 404]:
            raise NotFoundError(
                "404 from http backend for {namespace}/{filename}".format(
                    namespace=namespace, filename=filename
                )
            )
        if response.status_code != 200:
            raise ITSLoaderError(
                "{code} from http backend for {namespace}/{filename}".format(
                    code=response.status_code, namespace=namespace, filename=filename
                ),
                status_code=500,
            )

        # create an empty bytes object to store the image bytes in
        return BytesIO(response.content)

    @staticmethod
    def load_image(namespace, filename):
        """
        Loads image from http.
        """
        try:
            file_obj = HTTPLoader.get_fileobj(namespace, filename)
            img = Image.open(file_obj)

        except NotFoundError as error:
            raise NotFoundError("An error occurred: '%s'" % str(error))

        validate_image_type(img)

        return img
