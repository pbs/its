import io

from PIL import Image, ImageCms

# LOGGER = logging.getLogger(__name__)


class NormalizationError(Exception):
    pass


def normalize(image: Image) -> Image:
    output_mode = "RGB"
    # if the image has an alpha channel, preserve it
    if image.mode in ("RGBA", "LA"):
        output_mode = "RGBA"
        image = image.convert("RGBA")
    if "icc_profile" in image.info:
        fmt = image.format
        input_icc_profile = io.BytesIO(image.info["icc_profile"])
        output_icc_profile = ImageCms.createProfile("sRGB")
        try:
            image = ImageCms.profileToProfile(
                image, input_icc_profile, output_icc_profile, outputMode=output_mode
            )
        except ImageCms.PyCMSError:
            raise NormalizationError("failed to transform icc profile")
        image.format = fmt
    return image
