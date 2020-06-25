import logging
from io import BytesIO

import boto3
from botocore.exceptions import ClientError
from PIL import Image

from ..errors import NotFoundError
from ..settings import NAMESPACES
from ..util import validate_image_type
from .base import BaseLoader

LOGGER = logging.getLogger(__name__)


class S3Loader(BaseLoader):

    slug = "s3"
    parameter_name = "bucket"

    @staticmethod
    def get_fileobj(namespace, filename):
        """
        Given a namespace (or directory name) and a filename,
        returns a file-like or bytes-like object.
        """
        # get the s3 resource
        s3_resource = boto3.resource("s3")

        config = NAMESPACES[namespace]
        path = config.get("path", namespace).strip("/")
        key = "CORE/its-staging/{path}/{filename}".format(path=path, filename=filename).strip("/")
        bucket_name = config[S3Loader.parameter_name]
        s3_object = s3_resource.Object(bucket_name=bucket_name, key=key)

        # create an empty bytes object to store the image bytes in
        file_obj = BytesIO()
        s3_object.download_fileobj(file_obj)

        return file_obj

    @staticmethod
    def load_image(namespace, filename):
        """
        Loads image from AWS S3 bucket.
        """
        try:
            file_obj = S3Loader.get_fileobj(namespace, filename)
        except ClientError as error:
            error_code = error.response["Error"]["Code"]

            if error_code == "404":
                raise NotFoundError("An error occurred: '%s'" % str(error))

            # S3 can return 403 errors if the application lacks ListBucket
            # permissions for the relevant s3 bucket
            # https://stackoverflow.com/questions/19037664/how-do-i-have-an-s3-bucket-return-404-instead-of-403-for-a-key-that-does-not-e
            if error_code == "403":
                LOGGER.warning(
                    "403 from s3 bucket %s, the application probably lacks ListBucket permissions",
                    NAMESPACES[namespace][S3Loader.parameter_name],
                )
                raise NotFoundError("An error occurred: '%s'" % str(error))

            raise error

        image = Image.open(file_obj)

        validate_image_type(image)

        return image
