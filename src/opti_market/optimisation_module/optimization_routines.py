from typing import Any, TypedDict

import numpy as np
import pandas as pd
import pulp
from numpy.typing import NDArray

from opti_market.config_module import BATTERY, Markets, Opti_Market_Options, Output
from opti_market.output_module import output_results_opti, print_summary, save_summary

# ---
# ---
# Global variables
_MIN_DAY_ = 1440
_MIN_HR_ = 60
VarDict = dict[int, pulp.LpVariable]  # type alias: shorter annotations


# Useful class for handling multimarket
class MarketProblem(TypedDict):
    charge: VarDict
    discharge: VarDict
    res: int
    prices: NDArray[np.float64]


# ---
# ---
def select_range_prices(
    tar_markt: pd.DataFrame, date: pd.Timestamp, window: pd.Timedelta
) -> NDArray[np.float64]:
    """From the actual date, extract the price
    from the given market using the specified window

    Args:
        tar_markt (pd.DataFrame): target market
        date (pd.Timestamp): date to process
        window (pd.Timedelta):how many days

    Returns:
        NDArray[np.float64]: price lists
    """

    end = date + window

    price_index = (tar_markt["timestamp"] >= date) & (tar_markt["timestamp"] < end)

    prices = tar_markt.loc[price_index, "price_gbp_per_mwh"].to_numpy(dtype=np.float64)

    return prices


# ---
def add_market(
    prob: pulp.LpProblem, prices: NDArray[np.float64], res: int, market_number: int
) -> MarketProblem:
    periods = range(len(prices))
    return MarketProblem(
        charge=prob.add_variable_dicts(
            f"charge_{market_number}", periods, lowBound=0.0
        ),
        discharge=prob.add_variable_dicts(
            f"discharge_{market_number}", periods, lowBound=0.0
        ),
        res=res,
        prices=prices,
    )


# ---
def battery_confg(
    prob: pulp.LpProblem, bat: BATTERY, time_vec_len: int
) -> dict[str, dict[int, pulp.LpVariable]]:
    # Defining output data

    charge_binary = prob.add_variable_dicts(
        "charge_binary", range(time_vec_len), cat="Binary"
    )
    energy_bat = prob.add_variable_dicts(
        "effective_bat_pwr",
        range(time_vec_len + 1),
        lowBound=0.0,
        upBound=bat.effective_max_storage_vol,
    )
    config_bat: dict[str, dict[int, pulp.LpVariable]] = {
        "charge_binary": charge_binary,
        "energy_bat": energy_bat,
    }

    return config_bat


# ---
def configure_problem(
    name_problem: str,
    bat: BATTERY,
    mar: Markets,
    opti_mar: Opti_Market_Options,
    sim_cycle_sd: pd.Timestamp,
    opti_interval: int,
    energy_start: float,
) -> tuple[pulp.LpProblem, dict[str, MarketProblem], dict[str, VarDict]]:
    # Temporary variable
    mkrt_prb: dict[str, MarketProblem] = {}
    # update battery

    # Initialise the problem
    prob = pulp.LpProblem(name_problem, pulp.LpMaximize)
    t_vc = int((_MIN_DAY_ * opti_mar.window_day.days) / mar.dt)
    dt_hr = mar.dt / _MIN_HR_
    bat_prb = battery_confg(prob=prob, bat=bat, time_vec_len=t_vc)
    time_step = range(t_vc)
    # Set the market variables
    for i in range(1, mar.n_market + 1):
        name_market = f"market_n{i}"
        res = int(mar.dt_steps[i - 1])

        prices = select_range_prices(
            getattr(mar, name_market), date=sim_cycle_sd, window=opti_mar.window_day
        )

        mkrt_prb[name_market] = add_market(
            prob=prob, prices=prices, res=res, market_number=i
        )
    # Configure the main problems
    # Objectives function
    total_energy_uncharged = pulp.lpSum(
        dt_hr * m["discharge"][t // m["res"]] / bat.get_spec_battery("discharge_eff")
        for m in mkrt_prb.values()
        for t in time_step
    )
    # Total profit
    total_profit = pulp.lpSum(
        dt_hr
        * float(m["prices"][t // m["res"]])
        * (m["discharge"][t // m["res"]] - m["charge"][t // m["res"]])
        for m in mkrt_prb.values()
        for t in time_step
    )
    # Constraint
    # TO DO: find a clever solution to say per each day the total_energy_uncharge must be lower than
    eta_cha = bat.get_spec_battery("charge_eff")
    eta_dch = bat.get_spec_battery("discharge_eff")
    max_pow = bat.effective_max_storage_vol
    max_dch = bat.get_spec_battery("max_discharge_rate")
    max_cha = bat.get_spec_battery("max_charge_rate")

    prob += total_energy_uncharged <= opti_mar.max_cycles * max_pow, "cycle_day_limit"
    if opti_interval == 0:
        prob += (
            bat_prb["energy_bat"][0] == bat.initial_charge * max_pow,
            "initial_energy",
        )
    else:
        prob += bat_prb["energy_bat"][0] == energy_start, "initial_energy"
    prob += total_profit

    for i in time_step:
        charge, discharge = 0, 0
        for m in mkrt_prb.values():
            charge += m["charge"][i // m["res"]]
            discharge += m["discharge"][i // m["res"]]
        # --
        prob += bat_prb["energy_bat"][i + 1] == bat_prb["energy_bat"][i] + dt_hr * (
            charge * eta_cha - discharge / eta_dch
        )
        prob += charge <= max_cha * (bat_prb["charge_binary"][i])
        prob += discharge <= max_dch * (1 - bat_prb["charge_binary"][i])

    return prob, mkrt_prb, bat_prb


# ---
def solve_problem(
    opti_opt: Opti_Market_Options, bat: BATTERY, markt: Markets, output: Output
) -> None:

    interval = opti_opt.end_date - opti_opt.start_date
    n_opt_max = int(interval / opti_opt.window_day)
    start = opti_opt.start_date
    start_energy = 0

    total_profit = 0.0

    market_names = [f"market_n{i}" for i in range(1, markt.n_market + 1)]
    summary: dict[str, Any] = {
        "start_date": opti_opt.start_date,
        "end_date": opti_opt.end_date,
        "optimization_window": opti_opt.window_day,
        "battery_model": bat.get_spec_battery("model_name"),
        "total_revenue": 0.0,
        "final_energy_mwh": 0.0,
        "market_revenues": {name: 0.0 for name in market_names},
        "battery_cyles": 0.0,
        "total_energy_left_mwh": 0.0,
        "effective_max_pow_mw": 0.0,
    }

    for i in range(n_opt_max):
        prob, mkrt_prb, bat_prb = configure_problem(
            name_problem=f"Dispatch_Battery_n{i}",
            bat=bat,
            mar=markt,
            opti_mar=opti_opt,
            sim_cycle_sd=start,
            opti_interval=i,
            energy_start=start_energy,
        )
        stats = prob.solve(pulp.HiGHS(msg=False))
        status = stats.status.name
        assert status == "Optimal", status
        # --- Save the raw data set and the windows average
        output_results_opti(
            output=output,
            bat_cfg=bat_prb,
            markt=mkrt_prb,
            prob=prob,
            time_information=(start, markt.dt, opti_opt.window_day),
            summary=summary,
        )
        # -- Update the data for starting an other optimization window
        energy = np.array(
            [
                bat_prb["energy_bat"][t].value()
                for t in range(len(bat_prb["energy_bat"]))
            ]
        )
        final_energy = energy[-1]  # state at the end -> next window
        steps = np.diff(energy)
        discharged = -steps[steps < 0].sum()  # flow during the window, positive
        bat.update_state_battery(dE=-discharged)  # your method expects it negative
        start_energy = min(max(final_energy, 0.0), bat.effective_max_storage_vol)
        total_profit = total_profit + float(pulp.value(prob.objective))
        start = start + opti_opt.window_day
    print(
        f"    TOTAL. {total_profit:.2f} profit for {opti_opt.start_date} to {opti_opt.end_date}",
    )
    summary["total_revenue"] = total_profit
    summary["effective_max_pow_mw"] = bat.effective_max_storage_vol
    summary["battery_cyles"] = bat.total_number_cycle
    summary["final_energy_mwh"] = start_energy
    print_summary(summary)
    save_summary(summary=summary, output=output)


# ---
