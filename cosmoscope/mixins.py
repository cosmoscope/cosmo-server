"""Registries used in package."""
import uuid
from .store import Store


class StoreRegistry(type):
    """
    When added to a class, automatically adds instances of that class to the
    central storage database.
    """
    def __call__(cls, *args, **kwargs):
        # Import in the call function to avoid circular imports
        # from .store import store

        instance = super(StoreRegistry, cls).__call__(*args, **kwargs)

        # Assign the instance a unique identifier
        instance._identifier = str(uuid.uuid4())

        store.register(instance)

        return instance
