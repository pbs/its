from typing import Sequence, Union

from PIL import Image


class BaseTransform(object):

    """
    Generic image transform type class
    """

    slug: Union[None, str] = None  # unique string that identifies a given transform

    @staticmethod
    def apply_transform(
        img: Image.Image, parameters: Sequence[Union[str, int]]
    ) -> Image.Image:
        raise NotImplementedError

    @staticmethod
    def derive_parameters(query: str) -> Sequence[Union[str, int]]:
        raise NotImplementedError
