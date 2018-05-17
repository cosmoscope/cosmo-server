import logging
from functools import wraps

from astropy.io import registry as io_registry

from ..core.operation import FunctionalOperation


def reversible_operation(name):
    """Defines a function as a reversible operation."""
    context = dict()

    def decorator(func):
        from ..core.server import ServerAPI

        func_op = FunctionalOperation(func, context=context, name=name)
        # Associate the name of the function with the name of the class
        # instance
        func_op.__name__ = func.__name__

        # Add the wrapped function as a method on the class definition. This
        # creates an unbound method attached to the class definition.
        setattr(ServerAPI, func_op.__name__, staticmethod(func_op))

        # The following creates a bound method to the class definition.
        # from types import MethodType
        # setattr(ServerAPI, label or func.__name__, MethodType(func, ServerAPI))

        logging.info("Function %s has been added to server api.",
                     func_op.__name__)

        return func_op
    return decorator


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