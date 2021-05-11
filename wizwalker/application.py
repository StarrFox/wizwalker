from copy import copy
from functools import cached_property
from pathlib import Path
from typing import List

from wizwalker import utils
from .client import Client


class WizWalker:
    """
    Represents the main program and handles all clients
    """

    def __init__(self):
        self._managed_handles = []
        self.clients = []

    def __repr__(self):
        return f"<WizWalker {self.clients=}>"

    @cached_property
    def install_location(self) -> Path:
        """
        Wizard101 install location
        """
        return utils.get_wiz_install()

    @staticmethod
    def start_wiz_client():
        utils.start_instance()

    def get_new_clients(self) -> List[Client]:
        """
        Get all new clients currently not managed

        Returns:
            List of new clients added
        """
        all_handles = utils.get_all_wizard_handles()

        new_clients = []
        for handle in all_handles:
            if handle not in self._managed_handles:
                self._managed_handles.append(handle)

                new_client = Client(handle)
                self.clients.append(new_client)
                new_clients.append(new_client)

        return new_clients

    def remove_dead_clients(self) -> List[Client]:
        """
        Remove and return clients that are no longer running

        Returns:
             List of the dead clients removed
        """
        # so we can remove from self.clients
        clients_proxy = copy(self.clients)

        dead_clients = []
        for client in clients_proxy:
            if not client.is_running():
                dead_clients.append(client)
                self.clients.remove(client)

        return dead_clients

    # imagine using this method; cringe
    def get_ordered_clients(self) -> List[Client]:
        """
        Get client's ordered by their position on the screen

        Returns:
            List of the ordered clients
        """
        return utils.order_clients(self.clients)

    async def close(self):
        """
        Closes the application and all clients
        """
        for client in self.clients:
            await client.close()
