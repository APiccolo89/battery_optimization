from importlib.resources import files
from pathlib import Path

import numpy as np
import pytest
import pandas as pd 

from opti_market.config_module import read_market

# --- 
def test_read_market():
    path = Path(files("opti_market")).resolve().parents[1] / 'study_case'
    
    market1 = read_market('market1.csv',str(path))
    
    assert isinstance(market1,pd.DataFrame)
# --- 

if __name__ == '__main__':
    test_read_market()