from importlib.resources import files
from pathlib import Path

import numpy as np
import pytest
import pandas as pd 

from opti_market.config_module import read_configuration


def test_configuration():

    pathtoconfig = str(Path(files("opti_market")).resolve().parents[1] \
                     / 'base_configuration' / 'double_market.yml')
    
    config_sim = read_configuration(pathtoconfig)
    
    assert len(config_sim['markets'].keys()) == 2
    assert config_sim['battery']['model_name'] == 'bt001'