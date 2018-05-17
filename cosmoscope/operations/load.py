from astropy.io import registry as io_registry
import numpy as np

from ..core.data import Data
from ..interfaces.decorators import reversible_operation
from ..core.store import Store

__all__ = ['load_data_from_path']


@reversible_operation("Load Session")
def load_session_from_path(file_name, context):
    store = Store()
    store.open(file_name)
    context['file_name'] = file_name

@reversible_operation("Save Session")
def save_session_to_path(file_name, context):
    store = Store()
    store.save(file_name)
    context['patfile_nameh'] = file_name

@reversible_operation("Load Data from Path")
def load_data_from_path(path, context):
    data = Data(np.random.sample(100), name="Test Data")
    context['path'] = path