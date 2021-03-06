"""Contains main storage class and related functions."""
import copy
import logging
import uuid
import os
import sys
import glob

import pickle
import datetime

from .data import Data

SAVE_PATH = os.path.join(os.path.expanduser("~/.cosmoscope"), "sessions")


class StoreRegistry(type):
    """
    When added to a class, automatically adds instances of that class to the
    central storage database.
    """
    def __call__(cls, *args, **kwargs):
        instance = super(StoreRegistry, cls).__call__(*args, **kwargs)

        # Assign the instance a unique identifier
        instance._identifier = str(uuid.uuid4())

        # Register this data instance on the store
        store.register(instance)

        return instance


class Store(dict):
    """
    The store is the centralized location for managing and propagating changes
    throughout the application.

    Note
    ----
    This data store should not be accessed explicitly and instead should be
    only act as a mediary for the server/client.
    """
    def __init__(self, *args, **kwargs):
        super(Store, self).__init__(*args, **kwargs)
        # Define this session's id. This is used for saving and loading
        # serialized data
        self._session_id = str(datetime.datetime.utcnow())

    def open(self, name=None):
        """
        Opens a saved document and loads it as the current session.
        """
        # If no filename given, load the latest stored session
        if name is None:
            session_files = glob.glob(os.path.join(SAVE_PATH, '*.csm'))

            # If there are no stored session files, raise an error
            if len(session_files) == 0:
                raise LookupError("No filename provided and no stored "
                                  "sessions to load.")

            # Get the most recent file
            recent_session_file = max(session_files, key=os.path.getctime)

            open_path = os.path.join(SAVE_PATH, recent_session_file)
        else:
            open_path = os.path.join(SAVE_PATH, name)

        if os.path.exists(open_path):
            with open(open_path, 'rb') as f:
                self.update(pickle.load(f))
        else:
            raise IOError("No file named '%s'.", name)

    def save(self, filename=None):
        """
        Serializes the current document to the users' drive.
        """
        file_path = os.path.join(SAVE_PATH, "{:s}.csm".format(filename or self._session_id))

        if not os.path.exists(SAVE_PATH):
            os.mkdir(SAVE_PATH)

        with open(file_path, 'wb') as f:
            pickle.dump(self, f)

    def __getitem__(self, key):
        """
        Retrieve a data object from the database.

        Returns
        -------
        : `~cosmoscope.core.data.Data`
            The data object.
        """
        data = super(Store, self).__getitem__(key)

        if data is None:
            logging.error("No stored data set with id %s", key)

        return data

    def register(self, data, overwrite=False):
        """
        Register `Data` object to be tracked by the database.
        """
        # identifier, data_dict = data.identifier, data.__class__.encode(data)

        if data.identifier in self and not overwrite:
            logging.warning("Data with identifier '%s' already exists in "
                "database. Pass 'overwrite=True' to overwrite.")
            return

        super(Store, self).__setitem__(data.identifier, data)

        logging.info("Data object has been added to database with id %s",
                     data.identifier)

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
            del self[identifier]

            logging.info(
                "Data object with id %s has been removed from database.",
                identifier)


# Initialize the cosmoscope store
store = Store()