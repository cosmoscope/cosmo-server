from astropy.io import registry as io_registry
import numpy as np

from ..core.data import Data
from ..interfaces.decorators import reversible_operation

__all__ = ['load_data_from_path']


@reversible_operation("Load Data from Path")
def load_data_from_path(path, filt, context):
    data = Data(np.random.sample(100), name="Test Data")
    context['path'] = (path, filt)


@load_data_from_path.register_undo
def unload_data(context):
    pass