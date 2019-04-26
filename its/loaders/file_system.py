from io import BytesIO
from pathlib import Path, PosixPath
from typing import Union

from PIL import Image
from PIL.JpegImagePlugin import JpegImageFile
from PIL.MpoImagePlugin import MpoImageFile
from PIL.PngImagePlugin import PngImageFile

from ..errors import NotFoundError
from ..util import validate_image_type
from .base import BaseLoader


class FileSystemLoader(BaseLoader):

    slug = "file_system"
    parameter_name = "folders"

    @staticmethod
    def load_image(
        namespace: str, filename: Union[PosixPath, str]
    ) -> Union[JpegImageFile, PngImageFile, MpoImageFile]:
        """
        Loads image from child folder of the git project folder serverless-its/
        """
        if isinstance(filename, PosixPath):
            filename = str(filename)
        # Path to the great grandparent directory of this file
        try:
            image_bytes = FileSystemLoader.get_fileobj(namespace, filename)
            image = Image.open(image_bytes)
        except FileNotFoundError:
            raise NotFoundError(
                "File Not Found at %s" % (Path(namespace + "/" + filename))
            )
        validate_image_type(image)

        return image

    @staticmethod
    def get_fileobj(namespace: str, filename: str) -> BytesIO:
        """
        Given a namespace (or directory name) and a filename,
        returns a file-like or bytes-like object.
        """
        api_root = Path(__file__).parents[1]
        image_path = Path(api_root / namespace / filename)
        return BytesIO(open(image_path, "rb").read())
