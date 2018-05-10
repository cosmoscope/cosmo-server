import logging

import gevent
import msgpack
from zerorpc import Publisher, Puller, Pusher, Server

from ..storage.store import Store
from .data import Data
from ..utils.singleton import Singleton

__all__ = ['ServerAPI']


class ServerAPI(metaclass=Singleton):
    """
    RPC server class.
    """

    def __init__(self, server_ip):
        self.publisher = Publisher()
        self.publisher.connect(server_ip)

    def undo(self):
        """
        Undo an operation popping from the stack and calling its `undo` method.
        """
        from .operations import Operation

        Operation.pop().undo()

    def redo(self):
        """
        Call the `redo` method on the latest operation to be added to stack.
        """
        from .operations import Operation

        Operation.redo()

    def testing(self, msg):
        print("Received 'testing' call on server")
        # self.publisher.testing("This is a test on client.")


def launch(server_ip=None, client_ip=None):
    server_ip = server_ip or "tcp://127.0.0.1:4242"
    client_ip = client_ip or "tcp://127.0.0.1:4243"

    # Setup the puller service
    server = Server(ServerAPI(server_ip))
    server.bind(client_ip)

    gevent.spawn(server.run)

    logging.info(
        "[server] Server is now listening on %s and sending on %s.",
        client_ip, server_ip)
