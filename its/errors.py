from typing import Any, Dict, Optional


class ITSError(Exception):
    """
    Base error class for ITS.
    """

    status_code: int = 400
    message: str = ""
    payload: Dict = dict()

    def __init__(
        self,
        error: str,
        *args: Any,
        status_code: Optional[int] = None,
        payload: Optional[Dict] = None
    ) -> None:
        super().__init__(error)

        self.message = self.message + error

        if payload:
            self.payload = payload

        if status_code:
            self.status_code = status_code

        if args:
            self.args = args


class ConfigError(ITSError):
    """
    Class for errors that deal with ITS settings.
    """

    status_code: int = 500
    message: str = "Configuration Error: "


class ITSLoaderError(ITSError):
    """
    General class for errors that occur in the ITS loader.
    """

    status_code: int = 400
    message: str = "ITSLoaderError: "


class ITSInvalidImageFileError(ITSLoaderError):
    pass


class ITSTransformError(ITSError):
    """
    General class for errors occuring while applying transforms.
    """

    status_code: int = 400
    message: str = "ITSTransformError: "


class NotFoundError(ITSError):
    """
    General class for existence errors.
    """

    status_code: int = 404
    message: str = "NotFoundError: "


class ITSClientError(ITSError):
    status_code: int = 400
    message: str = "ITSClientError: "
