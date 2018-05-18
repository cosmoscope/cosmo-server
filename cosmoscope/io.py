import logging
from functools import wraps

from astropy.io import registry as io_registry


def data_loader(label, identifier=None):
    """
    Add the function as an associated loader to a data type. This
    association gets stored in the astropy io registry.
    """
    def decorator(func):
        from ..core.data import Data

        logging.info("Added %s to custom loaders.", label)
        io_registry.register_reader(label, Data, func)
        io_registry.register_identifier(label, Data, identifier)

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator


def custom_writer(label):
    """
    Add a custom write function and associate it with a data object. This
    association gets stored in the astropy io registry.
    """
    def decorator(func):
        from ..core.data import Data

        logging.info("Added %s to custom writers.", label)
        io_registry.register_writer(label, Data, func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator
