from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

import numpy as np
import pandas as pd
import pulp

from opti_market.config_module import Output

if TYPE_CHECKING:                      
    from opti_market.optimisation_module.optimization_routines import MarketProblem

# --- 
# --- 
_SUMMARY_UNIT: dict[str, str] = {
    "start_date": "",
    "end_date": "",
    "optimization_window": "days",
    "battery_model": "",
    "total_revenue": "GBP",
    "final_energy_mwh": "MWh",
    "market_revenues": "GBP",          # same unit for every market
    "battery_cyles": "cycles",
    "total_energy_left_mwh": "MWh",
    "effective_max_pow_mw": "MWh",
}
# --- 
DATA_RAW = ("timestamp", "price_gbp_per_mwh", "charge_mw", "discharge_mw", "revenue_gbp")
DATA_WINDOW_ = ("start", "end", "total_revenue_gbp", "energy_end_mwh", "discharged_mwh")
# ---
# ---
def create_path(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)

    return path 
# ---
def save_data_raw(output:Output,
                   bat_cfg:dict[str, dict[int, pulp.LpVariable]],
                   markt:dict[str, MarketProblem],
                   prob:pulp.LpProblem,
                   time_information:tuple[pd.Timestamp,float,pd.Timedelta],
                   summary:dict[str,Any]) -> list[float]: 
    path = create_path(Path(output.path_to_save / 'Data_Raw'))
    # save markets data
    dt_min = time_information[1]                                   # model step, minutes
    total_revenue: list[float] = []
    for name, m in markt.items():
        period = pd.Timedelta(minutes=dt_min) * m["res"]           # length of one market period
        period_hours = period / pd.Timedelta(hours=1)
        start = time_information[0]

        rows : Any = []
        tot_rv = 0.0 
        for p in range(len(m["prices"])):
            charge = m["charge"][p].value() or 0.0
            discharge = m["discharge"][p].value() or 0.0
            reveneue = float(m["prices"][p]) * float(period_hours * (discharge - charge))
            rows.append({
                "timestamp": start,
                "price_gbp_per_mwh": float(m["prices"][p]),
                "charge_mw": charge,
                "discharge_mw": discharge,
                "revenue_gbp": reveneue,
            })
            start = start + period
            tot_rv = tot_rv + float(reveneue)
        summary['market_revenues'][name] += tot_rv 
        total_revenue.append(tot_rv)
        df = pd.DataFrame(rows, columns=DATA_RAW)
        file = Path(path) / f"{name}.csv"
        df.to_csv(file, mode="a", 
                  header=not file.exists(), 
                  index=False,
                  float_format="%.3f")
    return total_revenue
# --- 
def save_window(output:Output,
                   bat_prb:dict[str, dict[int, pulp.LpVariable]],
                   markt:dict[str, MarketProblem],
                   prob:pulp.LpProblem,
                   time_information:tuple[pd.Timestamp,float,pd.Timedelta]
                   ,total_revenue:list[float]) -> None: 
    
    path = create_path(Path(output.path_to_save / 'Data_Window'))
    start = time_information[0]
    end = time_information[0]+time_information[2]
    energy = bat_prb["energy_bat"]
    rows:Any = []
    values = np.array([pulp.value(energy[t]) for t in range(len(energy))])
    steps = np.diff(values)
    rows.append({
                 "start": start,
                 "end": end,
                "total_revenue_gbp": sum(total_revenue),
                "energy_end_mwh": values[-1],
                "discharged_mwh": -steps[steps < 0].sum(),
                })
    df = pd.DataFrame(rows, columns=DATA_WINDOW_)
    file_name = path / "window_optimisation_results.csv"
    df.to_csv(file_name, mode="a", 
              header=not file_name.exists(), 
              index=False, float_format="%.3f")
# ---
def output_results_opti(output:Output,
                   bat_cfg:dict[str, dict[int, pulp.LpVariable]],
                   markt:dict[str, MarketProblem],
                   prob:pulp.LpProblem,
                   time_information:tuple[pd.Timestamp
                                       ,float
                                       ,pd.Timedelta],
                   summary:dict[str,Any])->None:

    revenue = save_data_raw(output, bat_cfg, markt, prob, time_information,summary)
    save_window(output, bat_cfg, markt, prob, time_information, revenue)
# --- 
def summary_table(summary: dict[str, Any]) -> pd.DataFrame:
    """Turn the run summary into a table with one row per value: metric, value, unit."""
    rows = []
    for key, value in summary.items():
        unit = _SUMMARY_UNIT.get(key, "")
        if isinstance(value, dict):                     # market_revenues -> one row per market
            for name, sub_value in value.items():
                rows.append((f"{key}:{name}", sub_value, unit))
        else:
            rows.append((key, value, unit))
    return pd.DataFrame(rows, columns=["metric", "value", "unit"])
# --- 
def save_summary(summary: dict[str, Any], output: Output) -> Path:
    """Write the run summary as a CSV (metric, value, unit) and return its path."""
    
    file = Path(output.path_to_save) / "summary.csv"
    summary_table(summary).to_csv(file, index=False, float_format="%.2f")
    return file
# --- 

def print_summary(summary: dict[str, Any]) -> None:
    """Short report at the end of the simulation."""
    print(f"Total revenue: £{summary['total_revenue']:,.2f}")
    for name, value in summary["market_revenues"].items():
        print(f"  {name}: £{value:,.2f}")
    print(f"Battery cycles: {summary['battery_cyles']:,.2f}")
    print(f"Capacity at the end: {summary['effective_max_pow_mw']:2f} MWh")
    print(f"Energy at the end: {summary['final_energy_mwh']:.2f} MWh")