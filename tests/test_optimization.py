from importlib.resources import files
from pathlib import Path

import numpy as np
import pandas as pd

from opti_market.config_module import (
    BATTERY,
    Markets,
    Opti_Market_Options,
    Output,
    read_configuration,
)
from opti_market.optimisation_module import solve_problem


# ---
# --- 
def read_summary()->float:


    return revenue  
# ---
def test_integration_test_double():


    pathtoconfig = str(
        Path(str(files("opti_market"))).resolve().parents[1]
        / "base_configuration"
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



def test_integration_single_market_a():


    pathtoconfig = str(
        Path(str(files("opti_market"))).resolve().parents[1]
        / "base_configuration"
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

def test_integration_single_market_b():


    pathtoconfig = str(
        Path(str(files("opti_market"))).resolve().parents[1]
        / "base_configuration"
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