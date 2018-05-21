from ..store import store
from .client import SubscriberAPI

import jsonpickle

# Get the client singleton
subscriber = SubscriberAPI()


class Spectrum1D:
    """
    """
    def __init__(self, *args, **kwargs):
        packed_data_args = jsonpickle.encode(args)
        packed_data_kwargs = jsonpickle.encode(kwargs)

        # Create a new spectrum1d object passing along the provided arguments
        self._identifier = subscriber.client.create_data(
            {'args': packed_data_args, 'kwargs': packed_data_kwargs})

    def __getattribute__(self, name):
        data_attr = subscriber.client.query_data_attribute(self._identifier, name)
        data_attr = jsonpickle.decode(data_attr)

        return data_attr