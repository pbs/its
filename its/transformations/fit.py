import logging
import re
from typing import Sequence, Union

from PIL import Image, ImageOps

from ..errors import ITSClientError, ITSTransformError
from ..settings import DELIMITERS_RE, FOCUS_KEYWORD
from .base import BaseTransform

LOGGER = logging.getLogger(__name__)


def _fit_image(img, crop_width, crop_height, focal_x, focal_y):
    focal_x_percentage = focal_x / 100
    focal_y_percentage = focal_y / 100
    fitted_image = ImageOps.fit(
        img,
        (crop_width, crop_height),
        method=Image.ANTIALIAS,
        centering=(focal_x_percentage, focal_y_percentage),
    )
    fitted_image.format = img.format

    return fitted_image


def _derive_focal_point(
    img: Image.Image, query_parameters: Sequence[Union[str, int]]
) -> Sequence[Union[str, int]]:
    filename = img.info["filename"]
    # if FOCUS_KEYWORD is present in filename, do smart crop
    if filename.find(FOCUS_KEYWORD) >= 0:  # smart crop
        # match everything before and including the keyword
        pre_keyword_pattern = ".+?(" + FOCUS_KEYWORD + ")"
        # match the file type and period in the filename
        file_ext_patten = r"(\.).+"
        # Match and remove the non-argument filename parts using the patterns defined above
        filename = re.sub(pre_keyword_pattern, "", filename, flags=re.IGNORECASE)
        filename = re.sub(file_ext_patten, "", filename, flags=re.IGNORECASE)
        return re.split(DELIMITERS_RE, filename)

    if not query_parameters:
        # default crop, focal point is the center so 50% on the x & y axes
        return [50, 50]

    return query_parameters


class FitTransform(BaseTransform):

    slug = "fit"

    @staticmethod
    def derive_parameters(query: str) -> Sequence[str]:
        return re.split(DELIMITERS_RE, query)

    @staticmethod
    def apply_transform(
        img: Image.Image, parameters: Sequence[Union[str, int]]
    ) -> Image.Image:
        """
        Crops input img about a focal point.
        The default focal point is the center of the image.

        crop : image.png?crop=WWxHH
        focal crop : image.png?crop=WWxHHxFXxFY
        smart crop : image_focus-FXxFY.png?crop=WWxHH
        """
        if len(parameters) < 2:
            raise ITSClientError(error="crop requires width and height")

        crop_width, crop_height = parameters[:2]
        focal_point = _derive_focal_point(img, query_parameters=parameters[2:])

        # convert all arguments to ints since they're strings
        try:
            crop_width = int(crop_width)
            crop_height = int(crop_height)
            focal_x = int(focal_point[0])
            focal_y = int(focal_point[1])
        except ValueError:
            raise ITSClientError(
                "Invalid arguments supplied to Fit Transform."
                + "Crop takes takes WWxHHxFXxFY, "
                + " where WW is the requested width in pixels, "
                + "HH is the requested height in pixels, "
                + " and (FX, FY) is a pair of percentage values "
                + "indicating the optional focus point in the image. "
                + "The focus point can either be defined in the query or in the image filename."
            )

        if crop_width * crop_height > Image.MAX_IMAGE_PIXELS:
            raise ITSClientError(
                "{w}x{h} is too big".format(w=crop_width, h=crop_height)
            )

        if focal_x in range(0, 101) and focal_y in range(0, 101) and crop_height != 0:
            try:
                fitted_image = _fit_image(
                    img, crop_width, crop_height, focal_x, focal_y
                )
            except ITSTransformError as error:
                error_string = (
                    "Fit Transform with requested size %sx%s"
                    + " and requested focal point [%s, %s] failed."
                )
                LOGGER.error(error_string, crop_width, crop_height, focal_x, focal_y)
                raise error

        elif crop_height == 0:
            raise ITSClientError(error="Crop height must be greater than 0")

        else:
            # make sure focal args are percentages
            raise ITSClientError(error="Focus arguments should be between 0 and 100")

        return fitted_image
