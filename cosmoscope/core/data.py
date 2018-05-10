"""Contains core data container class and related functions."""
import logging
from abc import ABCMeta

from specutils import Spectrum1D

from ..storage.registeries import StoreRegistry

__all__ = ['Data']

_StoreRegistryProxy = type('StoreRegistryProxy', (StoreRegistry, ABCMeta), {})


class Data(Spectrum1D, metaclass=_StoreRegistryProxy):
    """Core data container class for cosmoscope."""

    def __init__(self, *args, name=None, **kwargs):
        super(Data, self).__init__(*args, **kwargs)

        self._identifier = None
        self._name = name

    @property
    def identifier(self):
        """Return `identifier` string for this data object."""
        return self._identifier

    @property
    def name(self):
        """Return user-provided name of object."""
        return self._name

    def to_dict(self):
        """Convert and return data object as a dictionary representation."""
        return dict(
            identifier=self.identifier,
            data=list(self.data),
            name=self.name,
            unit=str(self.unit or ""),
            uncertainty=list(self.uncertainty.array)
            if self.uncertainty is not None else None,
            uncertainty_type=self.uncertainty.uncertainty_type
            if self.uncertainty is not None else None,
            wcs=None,
            mask=list(self.mask) if self.mask is not None else None,
            meta=self.meta)

    @staticmethod
    def encode(obj):
        """
        Static method for encoding data as dictionary object. Used in `msgpack`
        for passing data along RPC.
        """
        if isinstance(obj, Data):
            return obj.to_dict()

        return obj

    @staticmethod
    def decode(obj):
        """
        Static method for decoding data from dictionary object. Used in
        `msgpack` for passing data along RPC.
        """
        try:
            obj = {k.decode('utf-8'): v for k, v in obj.items()}
            identifier = obj.pop('identifier')

            data = Data(**obj)
            setattr(data, '_identifer', identifier)

            return data
        except:
            logging.error(
                "Unable to decode object of type %s.", type(obj))
            return obj
