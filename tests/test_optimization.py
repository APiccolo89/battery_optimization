from importlib.resources import files
from pathlib import Path

import numpy as np
import pandas as pd

from opti_market.config_module import (
    BATTERY,
    Markets,
    Opti_Market_Options,
    read_configuration,
)
from opti_market.optimisation_module import solve_problem


def test_integration_test_single_market():


    pathtoconfig = str(
        Path(str(files("opti_market"))).resolve().parents[1]
        / "base_configuration"
        / "single_market.yml"
    )

    config_sim = read_configuration(pathtoconfig)
    # Battery
    bat = BATTERY(**config_sim["battery"])
    # Market
    markt = Markets(config_sim["markets"])
    # Solution options: {To Do: seeing the other options}
    opti_opt = Opti_Market_Options.read_optimisation_options(config_sim["sim_options"])
    # output
    output = solve_problem(opti_opt=opti_opt, markt=markt, bat=bat)

    assert isinstance(output, pd.DataFrame)

def test_integration_test_double_market():


    pathtoconfig = str(
        Path(str(files("opti_market"))).resolve().parents[1]
        / "base_configuration"
        / "single_market.yml"
    )

    config_sim = read_configuration(pathtoconfig)
    # Battery
    bat = BATTERY(**config_sim["battery"])
    # Market
    markt = Markets(config_sim["markets"])
    # Solution options: {To Do: seeing the other options}
    opti_opt = Opti_Market_Options.read_optimisation_options(config_sim["sim_options"])
    # output
    output = solve_problem(opti_opt=opti_opt, markt=markt, bat=bat)

    assert isinstance(output, pd.DataFrame)


if __name__ == "__main__":
    test_integration_test()
