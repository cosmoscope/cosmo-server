import logging

import signal
import gevent
import msgpack
from zerorpc import Publisher, Puller, Pusher, Server
import numpy as np

from .store import Store
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
        from .operation import Operation

        Operation.pop().undo()

    def redo(self):
        """
        Call the `redo` method on the latest operation to be added to stack.
        """
        from .operation import Operation

        Operation.redo()

    def register(self, msg):
        pass
        # self.publisher.testing("This is a test on client.")

    def load_data(self, path, format):
        """
        Load a data file given path and format.
        """
        import astropy.units as u
        # data = Data.read(path, format=format)
        data = Data(np.random.sample(100) * u.Jy, spectral_axis=np.linspace(1100, 1200, 100) * u.AA)

        self.publisher.data_loaded(data.identifier)

    def query_loader_formats(self):
        """
        Returns a list of available data loader formats.
        """
        from specutils import Spectrum1D
        from astropy.io import registry as io_registry

        all_formats = io_registry.get_formats(Spectrum1D)['Format']

        return all_formats

    def query_data(self, identifier, return_values):
        data = Store()[identifier]

        data_dict = {
            'name': data.name,
            'identifier': data.identifier,
            'spectral_axis': data.spectral_axis.value.tolist(),
            'spectral_axis_unit': data.spectral_axis.unit.to_string(),
            'flux': data.flux.value.tolist(),
            'unit': data.flux.unit.to_string()
        }

        return data_dict

def launch(server_ip=None, client_ip=None, block=True):
    server_ip = server_ip or "tcp://127.0.0.1:4242"
    client_ip = client_ip or "tcp://127.0.0.1:4243"

    # Setup the puller service
    server_api = ServerAPI(server_ip)
    server = Server(server_api)
    server.bind(client_ip)

    logging.info(
        "Server is now listening on %s and sending on %s.",
        client_ip, server_ip)

    gevent.signal(signal.SIGINT, server.stop)
    server.run() if block else gevent.spawn(server.run)