from importlib.resources import files
from pathlib import Path

import pandas as pd

from opti_market.config_module import Markets, read_configuration, read_market


# --- 
def test_market_class():
    from importlib.resources import files
    
    pathtoconfig = str(Path(str(files("opti_market"))).resolve().parents[1] \
                     / 'base_configuration' / 'double_market.yml')
    
    config_sim = read_configuration(pathtoconfig)

    markets = Markets(config_sim['markets'])
    
    assert len(markets.market_n1) == 52608
    assert len(markets.market_n2) == 26304 
    
# --- 
def test_read_market():
    path = Path(str(files("opti_market"))).resolve().parents[1] / 'study_case'
    
    market1 = read_market('market1.csv',str(path))
    
    assert isinstance(market1,pd.DataFrame)
# --- 
