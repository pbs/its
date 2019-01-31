import re
from typing import Sequence

from PIL import ImageFilter

from ..errors import ITSClientError
from ..settings import DELIMITERS_RE
from .base import BaseTransform


class BlurTransform(BaseTransform):

    slug = "blur"

    @staticmethod
    def derive_parameters(query: str) -> Sequence[str]:
        return re.split(DELIMITERS_RE, query)

    def apply_transform(img, parameters):
        """
        Blurs the image from value passed in parameters
        """

        try:
            blur = int(parameters[0])
        except ValueError:
            raise ITSClientError(error="blur requires valid value")

        return img.filter(ImageFilter.GaussianBlur(blur))
