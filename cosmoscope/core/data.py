"""Contains core data container class and related functions."""
import logging
from abc import ABCMeta

import jsonpickle
import numpy as np
from astropy.units import Quantity, Unit
from gwcs.coordinate_frames import SpectralFrame
from specutils import Spectrum1D

from ..interfaces.mixins import StoreRegistryMixin

__all__ = ['Data']

_StoreRegistryProxy = type('StoreRegistryProxy', (StoreRegistryMixin, ABCMeta), {})


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
            data=self.flux.value.tolist(),
            name=self.name,
            unit=str(self.unit or ""),
            uncertainty=self.uncertainty.array.tolist()
            if self.uncertainty is not None else None,
            uncertainty_type=self.uncertainty.uncertainty_type
            if self.uncertainty is not None else None,
            wcs=None,
            mask=list(self.mask) if self.mask is not None else None,
            meta=None #self.meta
            )

    @staticmethod
    def encode(obj, *args, **kwargs):
        """
        Static method for encoding data as dictionary object. Used in `msgpack`
        for passing data along RPC.
        """
        if isinstance(obj, Data):
            packed = jsonpickle.encode(obj, *args, **kwargs)

            # TODO: workaround for dealing with `Tabular1D` in which it's
            # stored as an inherited class of ABC
            packed = packed.replace('abc.Tabular1D', 'astropy.modeling.models.Tabular1D')

            return packed

        raise TypeError("Object must be of type 'Data', no '%s'.", obj.__class__)

    @staticmethod
    def decode(obj, *args, **kwargs):
        """
        Static method for decoding data from dictionary object. Used in
        `msgpack` for passing data along RPC.
        """
        data = jsonpickle.decode(obj, *args, **kwargs)

        # TODO: workaround for dealing with improper parsing of `_wcs_unit` in
        # the GWCS adapater class.
        if isinstance(data, Data) and hasattr(data.wcs, '_wcs_unit'):
            data.wcs._wcs_unit = data.wcs.wcs.output_frame.unit[0]

        return data


class UnitHandler(jsonpickle.handlers.BaseHandler):
    def flatten(self, obj, data):
        data['unit'] = obj.to_string()
        return data

    def restore(self, obj):
        return Unit(obj['unit'])


class SpectralFrameHandler(jsonpickle.handlers.BaseHandler):
    def flatten(self, obj, data):
        data['__dict__'] = obj.__dict__.copy()
        data['__dict__']['_unit'] = [x.to_string() for x in obj.unit]
        return data

    def restore(self, obj):
        spec_frame = SpectralFrame()
        spec_frame.__dict__ = obj['__dict__']
        spec_frame._unit = tuple([Unit(x) for x in obj['__dict__']['_unit']])
        return spec_frame


class QuantityHandler(jsonpickle.handlers.BaseHandler):
    def flatten(self, obj, data):
        data['value'] = obj.value
        data['unit'] = obj.unit.to_string()
        return data

    def restore(self, obj):
        return Quantity(obj['value'], unit=obj['unit'])


class NumpyArrayHandler(jsonpickle.handlers.BaseHandler):
    def flatten(self, obj, data):
        data['value'] = obj.tolist()
        data['dtype'] = obj.dtype.str
        return data

    def restore(self, obj):
        return np.array(obj['value'], dtype=obj['dtype'])


jsonpickle.handlers.register(Unit, UnitHandler)
jsonpickle.handlers.register(SpectralFrame, SpectralFrameHandler)
jsonpickle.handlers.register(Quantity, QuantityHandler)
jsonpickle.handlers.register(np.ndarray, NumpyArrayHandler)
