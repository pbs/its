import tempfile

from PIL import Image, ImageCms


def normalize(image: Image) -> Image:
    if "icc_profile" in image.info:
        fmt = image.format
        icc = tempfile.mkstemp(suffix=".icc")[1]
        with open(icc, "wb") as icc_file:
            icc_file.write(image.info["icc_profile"])
        srgb = ImageCms.createProfile("sRGB")
        image = ImageCms.profileToProfile(image, icc, srgb, outputMode="RGB")
        image.format = fmt
    return image
