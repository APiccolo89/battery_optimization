import shutil
from importlib.resources import files
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from opti_market.config_module import (
    BATTERY,
    Markets,
    Opti_Market_Options,
    Output,
    read_configuration,
)
from opti_market.optimisation_module import solve_problem

@pytest.fixture(scope="session", autouse=True)
def cleanup_output():
    yield
    pt = str(
        Path(str(files("opti_market"))).resolve().parents[1]
        / "results")


    shutil.rmtree(f"{pt}/VanKeken", ignore_errors=True)

# ---
# --- 
def read_summary(output: Output) -> tuple[float, float]:
    """Read the run summary and return (total revenue in GBP, battery cycles)."""
    file = Path(output.path_to_save) / "summary.csv"
    table = pd.read_csv(file).set_index("metric")["value"]

    revenue = float(table["total_revenue"])
    cycles = float(table["battery_cyles"])
    return revenue, cycles
# ---
def test_integration_test_double():

    pathtoconfig =  str(
        Path(str(files("opti_market"))).resolve().parents[1]
        / "tests" / "configuration_folder_tests"
        / "double_market.yml"
    )

    config_sim = read_configuration(pathtoconfig)
    # Battery
    bat = BATTERY(**config_sim["battery"])
    # Market
    markt = Markets(config_sim["markets"])
    # Solution options: {To Do: seeing the other options}
    opti_opt = Opti_Market_Options.read_optimisation_options(config_sim["sim_options"])
    output = Output.read_output_configuration(dict_config=config_sim["output"]
                                              , name_simulation=str(config_sim["name"]))
    
    
    solve_problem(opti_opt=opti_opt, markt=markt, bat=bat,output=output)
    # See if the total revenue and total cycles are the correct one
    rv,mc = read_summary(output=output)
    assert np.isclose(rv,1182.95,rtol=1e-2)
    assert np.isclose(mc,9.59,rtol=1e-2)
    
    



def test_integration_single_market_a():


    pathtoconfig = str(
        Path(str(files("opti_market"))).resolve().parents[1]
        / "tests" / "configuration_folder_tests"
        / "single_market_a.yml"
    )

    config_sim = read_configuration(pathtoconfig)
    # Battery
    bat = BATTERY(**config_sim["battery"])
    # Market
    markt = Markets(config_sim["markets"])
    # Solution options: {To Do: seeing the other options}
    opti_opt = Opti_Market_Options.read_optimisation_options(config_sim["sim_options"])
    output = Output.read_output_configuration(dict_config=config_sim["output"]
                                              , name_simulation=str(config_sim["name"]))
    
    
    solve_problem(opti_opt=opti_opt, markt=markt, bat=bat,output=output)
    # See if the total revenue and total cycles are the correct one
    rv,mc = read_summary(output=output)
    assert np.isclose(rv,937.06,rtol=1e-2)
    assert np.isclose(mc,9.48,rtol=1e-2)
    


def test_integration_single_market_b():


    pathtoconfig =  str(
        Path(str(files("opti_market"))).resolve().parents[1]
        / "tests" / "configuration_folder_tests"
        / "single_market_b.yml"
    )

    config_sim = read_configuration(pathtoconfig)
    # Battery
    bat = BATTERY(**config_sim["battery"])
    # Market
    markt = Markets(config_sim["markets"])
    # Solution options: {To Do: seeing the other options}
    opti_opt = Opti_Market_Options.read_optimisation_options(config_sim["sim_options"])
    output = Output.read_output_configuration(dict_config=config_sim["output"]
                                              , name_simulation=str(config_sim["name"]))
    
    
    solve_problem(opti_opt=opti_opt, markt=markt, bat=bat,output=output)
    # See if the total revenue and total cycles are the correct one
    rv,mc = read_summary(output=output)
    assert np.isclose(rv,1092.28,rtol=1e-2)
    assert np.isclose(mc,9.59,rtol=1e-2)
