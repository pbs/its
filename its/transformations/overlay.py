import logging
from pathlib import Path
from typing import Sequence

from PIL import Image

from ..errors import ConfigError, ITSClientError, ITSTransformError
from ..loaders import BaseLoader
from ..settings import NAMESPACES, OVERLAYS
from .base import BaseTransform

LOGGER = logging.getLogger(__name__)

OVERLAY_PROPORTION = 0.2


def get_loader(overlay_loader):

    loader_classes = BaseLoader.__subclasses__()

    loader = [loader for loader in loader_classes if loader.slug == overlay_loader]

    if not loader:
        raise ITSTransformError(
            "Not Found Error: Overlay Image Loader "
            + "with slug '%s' not found." % overlay_loader
        )
    if len(loader) > 1:
        raise ITSTransformError(
            "Configuration Error: Two or more Image Loaders "
            + "have slug '%s'." % overlay_loader
        )

    return loader


class OverlayTransform(BaseTransform):

    """
    Pastes a specified image over the input.

    image.png?overlay=overlay_img_path
    """

    slug = "overlay"

    @staticmethod
    def derive_parameters(query: str) -> Sequence[str]:
        # overlay transform does not take parameters, so we don't split this
        return [query]

    def apply_transform(self, img, parameters):
        if not parameters:
            raise ITSClientError("no overlay image supplied")

        if len(parameters) > 1:
            raise ValueError("overlay transform does not accept parameters")

        overlay = parameters[0]
        if not overlay:
            raise ITSClientError("no overlay image supplied")

        if "overlay" in NAMESPACES:
            loader = get_loader(NAMESPACES["overlay"]["loader"])
        else:
            raise ConfigError("No Backend has been set up for overlays.")

        if overlay.lower() not in OVERLAYS:
            namespace, *filename = overlay.strip("/").split("/")
            filename = Path("/".join(filename))
            overlay_image = loader[0].load_image(namespace, filename)
        else:
            namespace, *filename = OVERLAYS[overlay.lower()].split("/")
            filename = Path("/".join(filename))
            overlay_image = loader[0].load_image(namespace, filename)

        height = img.height
        overlay_size = int(height * OVERLAY_PROPORTION)
        resized_overlay = overlay_image.resize(
            (overlay_size, overlay_size), Image.ANTIALIAS
        )

        # Only the overlay has an alpha channel
        if img.mode != "RGBA":
            new_img = img.copy()
        else:
            # overlay and input img have alpha channels
            # make an image the size of the background with
            # RGBA mode and alpha composite new image with background
            # this maintains the alpha channel of the background
            new_img = Image.new("RGBA", img.size)
            new_img = Image.alpha_composite(new_img, img)

        padding_top = int(height * 0.05)
        padding_left = int(height * 0.05)
        new_img.paste(
            resized_overlay, (padding_top, padding_left), mask=resized_overlay
        )

        return new_img
