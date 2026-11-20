from dataclasses import InitVar, dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


# ---
# ---
@dataclass(frozen=True)
class Opti_Market_Options:
    window_day: pd.Timedelta
    start_date: pd.Timestamp
    end_date: pd.Timestamp
    max_cycles: float
    charge_min: float

    @classmethod
    def read_optimisation_options(cls, dict_config: dict[str, Any]):

        window_day = pd.Timedelta(days=dict_config["window_days"])
        start_date, end_date = _parse_dates(
            dict_config["start_date"], dict_config["end_date"], window=window_day
        )
        max_cycles = float(dict_config["max_cycles"])
        charge_min = float(dict_config["charge_min"])

        return cls(
            window_day=window_day,
            start_date=start_date,
            end_date=end_date,
            max_cycles=max_cycles,
            charge_min=charge_min,
        )


# ---
def _parse_dates(
    sd: str, ed: str | None, window: pd.Timedelta
) -> tuple[pd.Timestamp, pd.Timestamp]:
    """Parse the date and compute the number of intervals


    Args:
        sd (str): starting date
        ed (str | None): _description_
        window (pd.Timedelta): _description_

    Raises:
        ValueError:
           "The time interval is {interval_days.days} days and the window is "
           "{window.days} days: the interval must be a multiple of the window. "
           "Change start_date, end_date or window_days."

    Returns:
        tuple[pd.Timestamp, pd.Timestamp]: _description_
    """

    parsed_sd = pd.to_datetime(sd, yearfirst=True)

    if (ed is None) or (ed == sd):
        parsed_ed = parsed_sd + pd.Timedelta(days=1)
        print(
            f"No ending date has been provided, the simulation will be performed only for the date {sd}"
        )
    else:
        parsed_ed = pd.to_datetime(ed, yearfirst=True)

    interval_days = parsed_ed - parsed_sd

    if interval_days.days % window.days != 0:
        raise ValueError(
            f"The time interval is {interval_days.days} days and the window is "
            f"{window.days} days: the interval must be a multiple of the window. "
            f"Change start_date, end_date or window_days."
        )

    return parsed_sd, parsed_ed


# ---
# ---
