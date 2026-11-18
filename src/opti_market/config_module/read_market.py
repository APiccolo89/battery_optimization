import csv
from pathlib import Path

import numpy as np
import pandas as pd


# ---
def read_market(name:str, path:str)->pd.DataFrame:
    """Read the market csv file

    Args:
        name (str): name of the csv file
        path (str): path to the csv file

    Returns:
        market (pd.DataFrame): market data frame
    """
    
    if not name.endswith('.csv'):
        raise ValueError(f'{name} is not a csv file',
                         ' convert the market file into a .csv file')
    
    path_to_file = Path(path) / name
    
    if not path_to_file.exists():
        raise FileNotFoundError(f"Price file not found: {path}.")
    
    market = pd.read_csv(path_to_file, parse_dates=["timestamp"])
    
    return market
# --- 



    

if __name__ == '__main__':
    test_read_market()