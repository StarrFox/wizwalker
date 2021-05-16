from warnings import warn

from .client_handler import ClientHandler


# TODO: delete this file in 2.0
class WizWalker(ClientHandler):
    def __init__(self):
        super().__init__()
        warn(
            "The WizWalker class is depreciated and will be removed in 2.0; please use ClientHandler",
            DeprecationWarning,
        )
