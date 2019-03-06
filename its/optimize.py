import subprocess
import uuid
from math import floor
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, Dict, Optional

from PIL import Image, ImageFile
from PIL.JpegImagePlugin import JpegImageFile
from PIL.PngImagePlugin import PngImageFile
from PIL import ImageCms

from its.settings import DEFAULT_JPEG_QUALITY, PNGQUANT_PATH

from .errors import ITSClientError, ITSTransformError

ImageFile.MAXBLOCK = 2 ** 20  # for JPG progressive saving


def identify_best_format(img: Image.Image) -> str:
    identical_pixel_threshold = 0.001
    common_values_threshold = 50
    hist = img.histogram()
    total = sum(hist)
    common_vals = [v for v in hist if v / total > identical_pixel_threshold]
    if len(common_vals) < common_values_threshold:
        return "png"

    return "jpeg"


def optimize(img: Image.Image, query: Dict[str, str]) -> Image.Image:
    # the return format
    if "format" not in query:
        ext = img.format.lower()
    elif query["format"] == "auto":
        ext = identify_best_format(img)
    else:
        ext = query["format"]

    try:
        quality = int(query["quality"]) if "quality" in query else None
    except ValueError as error:
        raise ITSClientError("ITS Client Error: " + str(error))

    with NamedTemporaryFile(dir="/tmp/", delete=True) as tmp_file:
        if ext.lower() == "jpg":
            ext = "jpeg"

        # convert first, then optimize
        if ext.lower() == "jpeg":
            # convert to JPG and/or compress
            # need to convert to RGB first, then can save in any format
            if img.mode == "RGBA":
                new_img = Image.new("RGBA", img.size)
                new_img = Image.alpha_composite(new_img, img)
            img = img.convert("RGB")
            img = optimize_jpg(img, tmp_file, quality)
        elif ext.lower() in ["png", "webp"]:
            # convert from PNG, JPG and WEBP to formats other than JPG
            img = convert(img, ext, tmp_file)

        else:
            raise ITSClientError("ITS Client Error: Format must be jpeg, png or webp")

        # only optimize pngs if quality param is provided
        if img.format == "PNG" and quality is not None:
            img = optimize_png(img, tmp_file, quality)

    return img


# https://github.com/python/mypy/issues/3094 - _TemporaryFileWrapper from
# tempfile can't be imported for type annotation here
def convert(img: Image.Image, ext: str, tmp_file: Any) -> Image.Image:
    if ext.lower() == img.format.lower():  # same format so do nothing
        return img

    if img.format.lower() not in ["png", "webp", "jpeg"]:
        return img

    if img.mode in ["CMYK", "LA"]:
        img = img.convert("RGB")

    img.save(tmp_file.name, ext.upper())

    # reopen newly converted or compressed image
    return Image.open(tmp_file.name)


def optimize_jpg(
    img: JpegImageFile, tmp_file: Any, quality: Optional[int] = DEFAULT_JPEG_QUALITY
) -> JpegImageFile:
    if not quality:
        quality = DEFAULT_JPEG_QUALITY
    elif quality > 95:
        quality = 95  # 95 is the recommended upper limit on quality for JPEGs in PIL

    img.save(tmp_file.name, "JPEG", quality=quality, optimize=True, progressive=True)

    return Image.open(tmp_file.name)


def optimize_png(img: PngImageFile, tmp_file: Any, quality: int = 95) -> PngImageFile:
    output_path = "/tmp/" + str(uuid.uuid4())

    if quality >= 100:
        return img

    if quality % 10 == 0:
        speed = int(quality / 10)  # quality is inversely related to pngquant speed
    else:
        # each interval of 10 is related to one speed:
        # [90 - 99] --> speed 9
        speed = int(floor((quality - (quality % 10)) / 10))

    command = [
        PNGQUANT_PATH,
        "--strip",
        "--force",
        "--output",
        output_path,
        "-s" + str(speed),
        tmp_file.name,
    ]

    try:
        img.save(tmp_file.name, format=img.format)
        subprocess.check_output(command, stderr=subprocess.STDOUT)
        img = Image.open(output_path)
        if Path(output_path).exists():
            Path(output_path).unlink()
    except (OSError, subprocess.CalledProcessError) as error:
        raise ITSTransformError("ITSTransform Error: " + str(error))

    return img
