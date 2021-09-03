import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
from copy import copy
from functools import cached_property
from pathlib import Path
from typing import Optional

import wizwalker
from wizwalker import utils
from .client import Client


class ClientHandler:
    """
    Manages clients
    """

    def __init__(self, *, client_cls: type[Client] = Client):
        self.client_cls = client_cls

        self._managed_handles = []
        self.clients = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @cached_property
    def install_location(self) -> Path:
        """
        Wizard101 install location
        """
        return utils.get_wiz_install()

    @staticmethod
    def start_wiz_client():
        """
        Start a new client
        """
        utils.start_instance()

    def get_foreground_client(self) -> Optional[wizwalker.Client]:
        for client in self.clients:
            if client.is_foreground:
                return client

    def get_new_clients(self) -> list[Client]:
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

                new_client = self.client_cls(handle)
                self.clients.append(new_client)
                new_clients.append(new_client)

        return new_clients

    def remove_dead_clients(self) -> list[Client]:
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

    def get_ordered_clients(self) -> list[Client]:
        """
        Get client's ordered by their position on the screen

        Returns:
            List of the ordered clients
        """
        return utils.order_clients(self.clients)

    def activate_all_client_hooks(self, wait_for_ready: bool = True):
        """
        Activate hooks for all clients
        """
        with ThreadPoolExecutor() as executor:
            futures = []

            for client in self.clients:
                futures.append(
                    executor.submit(
                        client.activate_hooks, wait_for_ready=wait_for_ready
                    )
                )

            if wait_for_ready:
                concurrent.futures.wait(futures)

    def activate_all_client_mouseless(self):
        """
        Activates mouseless hook for all clients
        """
        for client in self.clients:
            client.mouse_handler.activate_mouseless()

    def close(self):
        """
        Closes all clients
        """
        for client in self.clients:
            client.close()
