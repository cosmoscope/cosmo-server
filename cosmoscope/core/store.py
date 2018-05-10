"""Contains main storage class and related functions."""
import copy
import logging
import uuid

import six

from .data import Data
from .singletons import Singleton


class Store(metaclass=Singleton):
    """
    The store is the centralized location for managing and propagating changes
    throughout the application.

    Note
    ----
    This data store should not be accessed explicitly and instead should be
    only act as a mediary for the server/client.
    """
    def __init__(self, *args, **kwargs):
        self._state = dict(*args, **kwargs)

    def register(self, data):
        """
        Register `Data` object to be tracked by the database.
        """
        self._state.setdefault('data', {}).setdefault(
            data.identifier, data.__class__.encode(data))

        logging.info("Data object has been added to store with id %s",
                     data.identifier)

    def get(self, identifier):
        """
        Retrieve a data object from the database.

        Returns
        -------
        : `~cosmoscope.core.data.Data`
            The data object.
        """
        data_dict = self._state.get(identifier)

        if data_dict is None:
            logging.error("No stored data set with id %s", identifier)

        return Data(**data_dict)

    def update(self, identifier, update_dict):
        """
        Updates the given storage pointer to a new data set.

        Returns
        -------
        : dict
            A python `dict` holding the differences between the old and new
            data objects.
        """
        data = self.get(identifier).to_dict()

        # Create a deep copy of the current data object so that it can be
        # compared with the updated data object, and the differences returned
        data_copy = copy.deepcopy(data)

        # Update the store dictionary object
        data.update(update_dict)

        return {k: data_copy[k] for k in set(data) - set(data_copy)}

    def unregister(self, identifier):
        """
        Removes data object tracking from the database.
        """
        if self.get(identifier) is not None:
            del self._state[identifier]

            logging.info(
                "Data object with id %s has been removed from database.",
                identifier)
