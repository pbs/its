from typing import Union


class BaseLoader:
    """
    Generic file loader class
    """

    slug: Union[None, str] = None
    parameter_name: Union[None, str] = None

    def __init__(self, arg):
        super(BaseLoader, self).__init__()
        self.arg = arg

    @staticmethod
    def load_image(namespace, filename):
        """
        Given a namespace (or directory name) and a filename, loads a file.
        """
        raise NotImplementedError

    @staticmethod
    def get_fileobj(namespace, filename):
        """
        Given a namespace (or directory name) and a filename,
        returns a file-like or bytes-like object.
        """
        raise NotImplementedError
