"""Market price timeseries and their common time step and time frame."""

from dataclasses import InitVar, dataclass, field
from math import gcd
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

_MIN_HOUR_: float = 60
_SEC_MIN_: float = 60
_FRACTION_HOUR: tuple[float, ...] = (1 / 4, 1 / 2, 3 / 4, 1.0)


# ---
# ---
@dataclass
class Markets:
    """Price timeseries of up to six markets and their common time grid.

    Attributes:
        markets (dict): market configurations, each with "prices_file" and
            "path_to_file" entries (init only).
        n_market (int): number of markets.
        market_n1 ... market_n6 (pd.DataFrame): price timeseries of each market;
            unused slots are None.
        common_start (pd.Timestamp): latest first timestamp among the markets.
        common_end (pd.Timestamp): earliest last timestamp among the markets.
        dt (float): common time step (minutes), the greatest common divisor of
            the market time steps.
        dt_steps (list[int]): number of common time steps in one period of each
            market.
    """

    markets: InitVar[dict[str, Any]]
    n_market: int = field(init=False)
    market_n1: pd.DataFrame = field(init=False)
    market_n2: pd.DataFrame = field(init=False)
    market_n3: pd.DataFrame = field(init=False)
    market_n4: pd.DataFrame = field(init=False)
    market_n5: pd.DataFrame = field(init=False)
    market_n6: pd.DataFrame = field(init=False)
    common_start: pd.Timestamp = field(init=False)
    common_end: pd.Timestamp = field(init=False)
    dt: float = 0.0
    dt_steps: list[int] = field(init=False)

    # ---
    def __post_init__(self, markets: dict[str, Any]):
        """Read the price file of each market and set the common time grid.

        Args:
            markets (dict): market configurations, each with "prices_file" and
                "path_to_file" entries.

        Raises:
            ValueError: if more than six markets are given.
        """
        self.n_market = len(markets)
        if self.n_market > 6:
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

        self._extract_dt()
        self._check_initial_final_date_markets()

    # Find the common time interval
    def _check_initial_final_date_markets(self) -> None:
        """Find the common time frame of the markets.

        Set common_start to the latest first timestamp and common_end to the
        earliest last timestamp among the markets.

        Raises:
            ValueError: if the markets do not overlap in time.
        """

        start: list[pd.Timestamp] = []
        end: list[pd.Timestamp] = []
        for k in range(self.n_market):
            a = getattr(self, f"market_n{k + 1}")
            start.append(a["timestamp"].min())
            end.append(a["timestamp"].max())

        self.common_start = max(start)
        self.common_end = min(end)

        if self.common_start >= self.common_end:
            raise ValueError("The markets do not overlap in time")

    # ---
    def _extract_dt(self) -> None:
        """Collect all the markets, compute the dt for each market and
        choose the minimum denominator.
        Before that, check if the prices are in any fraction of an hour;
        the accepted fractions of an hour are 15/30/45/60 min.
        total minutes day: 1440 % (_FRACTION_) = 64,48,32,24
        """
        dt_buf: float = 0.0
        dt_list: list[int] = []

        for i in range(self.n_market):
            # mrkt
            mrkt = getattr(self, f"market_n{i + 1}")
            # compute dt in minutes
            dt_buf = mrkt["timestamp"].diff().mean().total_seconds() / _SEC_MIN_

            res = dt_buf - np.floor(dt_buf)
            if not np.isclose(res, 0.0, rtol=1e-2):
                raise ValueError("Check the timeseries, the timesteps are not even")

            dt_buf = int(np.floor(dt_buf))
            if dt_buf / _MIN_HOUR_ not in _FRACTION_HOUR:
                raise ValueError(
                    f"market_n{i} has dt that is not a hour fraction (1/4,1/2,3/4,1.0)"
                )

            dt_list.append(dt_buf)

        self.dt = gcd(*dt_list)
        self.dt_steps = [d // self.dt for d in dt_list]


# ---
# ---
def read_market(name: str, path: str) -> pd.DataFrame:
    """Read the market csv file.

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
# ---
