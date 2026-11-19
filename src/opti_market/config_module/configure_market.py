from dataclasses import InitVar, dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd


# --- 
# ---
@dataclass
class Markets:
    markets: InitVar[dict[str, Any]]
    n_market: int = field(init=False)
    market_n1: pd.DataFrame = field(init=False)
    market_n2: pd.DataFrame = field(init=False)
    market_n3: pd.DataFrame = field(init=False)
    market_n4: pd.DataFrame = field(init=False)
    market_n5: pd.DataFrame = field(init=False)
    market_n6: pd.DataFrame = field(init=False)
    # ---
    def __post_init__(self, markets: dict[str, Any]):
        n_market = len(markets)
        if n_market > 6:
            raise ValueError("The maximum market per battery is 6. Reduce the markets")
        cnt = 1
        # Initialise the class
        for k in range(1, 7):
            setattr(self, f"market_n{k}", None)
        # Loop over the markets
        for m in markets.values():
            setattr(
                self, f"market_n{cnt}", read_market(m["prices_file"], m["path_to_file"])
            )
            cnt = cnt + 1
# ---
def read_market(name: str, path: str) -> pd.DataFrame:
    """Read the market csv file

    Args:
        name (str): name of the csv file
        path (str): path to the csv file

    Returns:
        market (pd.DataFrame): market data frame
    """

    if not name.endswith(".csv"):
        raise ValueError(
            f"{name} is not a csv file", " convert the market file into a .csv file"
        )

    path_to_file = Path(path) / name

    if not path_to_file.exists():
        raise FileNotFoundError(f"Price file not found: {path}.")

    market = pd.read_csv(path_to_file, parse_dates=["timestamp"])

    return market
# ---
