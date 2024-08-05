"""
SMAP Services Package
"""

import os
import yaml

def load_config(path):
    with open(path, 'r') as file:
        return yaml.safe_load(file)
    
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.yaml')
CONFIG = load_config(CONFIG_PATH)

# Define package-level variables or constants
__version__ = '0.0.1'
__author__ = 'tylew, brmurray, Matthew Graham'
__email__ = 'tyler@clean-coalition.org'

# Import the main functions from the submodules
from smap_package.smap_client import SMAP_Client

# imported when "from smap_services import *" is used.
__all__ = [
    'SMAP_Client',
    'CONFIG'
]