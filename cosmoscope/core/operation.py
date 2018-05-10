import abc
import logging
from functools import wraps


class Operation(metaclass=abc.ABCMeta):
    """
    Operations are reversible actions that are performed on data sets. In order
    to implement an operation, the inheriting class must override both the
    `__call__` method (the forward operation), and the `undo` method (the back-
    ward operation).
    """
    _stack = []
    _previous_action = None

    @abc.abstractmethod
    def __call__(self, *args, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def undo(self, *args, **kwargs):
        raise NotImplementedError

    def register_undo(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        self._undo = wrapper

        return wrapper

    @classmethod
    def pop(cls, index=-1):
        """
        Pop the last operation off the stack and return it.

        Parameters
        ----------
        index : int
            Index at which to pop.

        Returns
        -------
        last_op : :class:`~Operation`
            The operation from the give index popped from stack.
        """
        last_op = cls._stack.pop(index)
        cls._previous_action = last_op

        return last_op

    @classmethod
    def redo(cls):
        cls._previous_action()


class FunctionalOperation(Operation):
    def __init__(self, function, context=None, name=None, *args, **kwargs):
        if not callable(function):
            raise TypeError("{} is not callable.".format(function))

        super(FunctionalOperation, self).__init__()

        self._function = function
        self._context = context or {}
        self._name = name if name is not None else function.__name__
        self._args = args
        self._kwargs = kwargs
        self._undo = lambda x: logging.error(
            "No undo registered for %s", function)

    def __call__(self, *args, **kwargs):
        self._stack.append(self)

        kwargs.update({'context': self._context})

        return self._function(*args, **kwargs)

    @property
    def name(self):
        return self._name

    def undo(self, *args, **kwargs):
        args = () if args is None else args
        kwargs = {} if kwargs is None else kwargs
        kwargs.update({'context': self._context})

        print("undoing {}".format(self.name), self._context)

        return self._undo(*args, **kwargs)
