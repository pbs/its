"""
Script to apply transformations to validated images.
"""
import re
from io import BytesIO
from typing import Dict, Union

from PIL.JpegImagePlugin import JpegImageFile
from PIL.PngImagePlugin import PngImageFile

from .transformations import (
    BlurTransform,
    FitTransform,
    OverlayTransform,
    ResizeTransform,
)


def process_transforms(
    img: Union[JpegImageFile, PngImageFile, BytesIO], query: Dict[str, str]
) -> Union[JpegImageFile, PngImageFile, BytesIO]:
    """
    View that returns an image transformed according to the
    query options in the request string.
    """
    if not query:  # no transforms; return image as is
        return img

    if isinstance(img, BytesIO):  # SVG, return image as is
        return img

    if query.get("crop"):
        query["fit"] = query.pop("crop")

    img_info = img.info
    transform_order = [BlurTransform, ResizeTransform, FitTransform, OverlayTransform]

    # loop through the order dict and apply the transforms
    for transform in transform_order:
        slug = transform.slug
        if slug in query:
            parameters = transform.derive_parameters(query[slug])
            img = transform.apply_transform(img, parameters)

    if img.format is None and "filename" in img_info.keys():
        # attempt to grab the filetype from the filename
        file_type = re.sub(r".+?(\.)", "", img_info["filename"], flags=re.IGNORECASE)
        if file_type.lower() == "jpg" or file_type.lower() == "jpeg":
            img.format = "JPEG"
        else:
            img.format = file_type.upper()

    return img
