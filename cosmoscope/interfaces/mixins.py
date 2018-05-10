"""Registries used in package."""
import uuid


class StoreRegistryMixin(type):
    """
    When added to a class, automatically adds instances of that class to the
    central storage database.
    """
    def __call__(cls, *args, **kwargs):
        # Import in the call function to avoid circular imports
        from ..core.store import Store

        instance = super(StoreRegistryMixin, cls).__call__(*args, **kwargs)

        # Assign the instance a unique identifier
        instance._identifier = str(uuid.uuid4())

        store = Store()
        store.register(instance)

        return instance
