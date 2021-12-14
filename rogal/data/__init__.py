from .core import DataParsers, DataStore

parsers = DataParsers()
data_store = DataStore()

from ..colors import data_parsers
from ..console import data_parsers
from ..events import data_parsers
from ..tiles_sources import data_parsers
from ..ui_toolkit import data_parsers

from .data import *

