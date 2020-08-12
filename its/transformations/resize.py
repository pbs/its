import re
from math import floor
from typing import Sequence

from PIL import Image

from ..errors import ITSClientError
from ..settings import DELIMITERS_RE
from .base import BaseTransform


class ResizeTransform(BaseTransform):

    slug = "resize"

    @staticmethod
    def derive_parameters(query: str) -> Sequence[str]:
        return re.split(DELIMITERS_RE, query)

    def apply_transform(self, img, parameters):
        """
        Resizes input image while maintaining aspect ratio.
        """
        option = ''
        if len(parameters) == 2:
            width, height = parameters
        elif len(parameters) == 3:
            width, height, option = parameters
        else:
            raise ITSClientError(
                "Missing width or height. Both width and height are required"
            )

        if img.width == 0 or img.height == 0:
            raise ITSClientError(
                "Invalid arguments supplied to Resize Transform."
                "Input image cannot have zero width nor zero height."
            )

        try:
            width = int(width) if width != "" else None
            height = int(height) if height != "" else None
        except ValueError:
            raise ITSClientError(
                "Invalid arguments supplied to Resize Transform. "
                "Resize takes WWxHH, WWx, or xHH,"
                " where WW is the requested width and "
                "HH is the requested height. Both must be integers."
            )

        if width is None and height is None:
            raise ITSClientError(
                "Invalid arguments supplied to Resize Transform."
                "Resize takes WWxHH, WWx, or xHH,"
                " where WW is the requested width and "
                "HH is the requested height. Both must be integers."
            )

        if width and height and width * height > Image.MAX_IMAGE_PIXELS:
            raise ITSClientError("{w}x{h} is too big".format(w=width, h=height))

        if width is None:
            tgt_width = floor((img.width / img.height) * height)
            tgt_height = height
        elif height is None:
            tgt_height = floor((img.height / img.width) * width)
            tgt_width = width
        else:
            # width and height are the max width and max height expected
            # calculate a resize ratio between them and the original sizes
            ratio = min(width / img.width, height / img.height)
            # make sure target is at least one pixel wide
            tgt_width = max(floor(img.width * ratio), 1)
            tgt_height = max(floor(img.height * ratio), 1)

        if option == 'no-scale-up' and (
                tgt_width > img.width or
                tgt_height > img.height
            ):
            tgt_height = img.height
            tgt_width = img.width

        resized = img.resize([tgt_width, tgt_height], Image.ANTIALIAS)

        # make sure we don't lose format data
        resized.format = img.format

        return resized
