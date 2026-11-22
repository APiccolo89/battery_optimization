"""
Definition of options for the input configuration file.

'man':'mandatory', => If it is not defined, the program is preventevely blocked
'opt': 'fully optional, if anything is defined, the default value are applied'
"""

from importlib.resources import files
from pathlib import Path
from typing import Any, Literal

import yaml

from opti_market.config_module.configure_battery import BATTERY
from opti_market.config_module.configure_market import Markets
from opti_market.config_module.configure_output import Output
from opti_market.config_module.configure_simulation import Opti_Market_Options

# --> Global variables : to move in utils after the first draft of the code is done
#     1. To avoid duplicate logic, and having a centralised global_par.py in utils.py
# ---
# ---
OptionKind = Literal["man", "opt"]
OptionValue = str | Any | None
# ---
# The lowest level of the dictionary always
_BATTERY_INPUT_: dict[str, tuple[OptionKind, OptionValue]] = {
    "model_name": ("man", None),
    "degradation_model": ("opt", "linear"),
    "initial_cycles": ("opt", 0),
    "initial_age": ("opt", 0),
    "initial_charge": ("opt", 0.5),
    "name_field": ("opt", "battery"),
}
# ---
_MARKET_INPUT_: dict[str, tuple[OptionKind, OptionValue]] = {
    "prices_file": ("man", None),
    "path_to_file": ("opt", None),
    "packaged_data": ("opt", True),
    "name_field": ("opt", "market"),
}
# ---
_SIMULATION_INPUT_: dict[str, tuple[OptionKind, OptionValue]] = {
    "start_date": ("man", None),  # if no start_date is set, throw an error.
    "end_date": (
        "opt",
        None,
    ),  # if no end-date is set, it is automatically set for the day
    "max_cycles": (
        "opt",
        1e9,
    ),  # Flag value, it will never hits 1 bilion charge cycle in a day.
    "charge_min": (
        "opt",
        0.0,
    ),  # I wanted to put a minimal residual charge, but for preserving the battery, also max_cycle can work.
    "window_days": ("opt", 1),
}
_OUTPUT_INPUT_ : dict[str, tuple[OptionKind, OptionValue]] = {
    'path_to_save': ('opt',None),
    'basic_plot': ('opt',False),
    'default_location': ('opt',True),
    'clean_option': ('opt',True)
        }
# ---
# ---
def read_simulation_config(inp_dict: dict[str, Any]) -> dict[str, Any]:

    sim_config = check_input(inp_dict=inp_dict, par=_SIMULATION_INPUT_)

    return sim_config

# --- 
def read_simulation_output(inp_dict: dict[str, Any]) -> dict[str, Any]:

    output_configuration = check_input(inp_dict=inp_dict, par=_OUTPUT_INPUT_)
    # Safe Guard. 
    if output_configuration['path_to_save'] == '':
        output_configuration['path_to_save'] = None

    if (output_configuration['path_to_save'] is not None
        and (output_configuration['default_location'])):
        raise ValueError('The default location cannot be True, if a path_to_save is specified')

    return output_configuration


# ---
def read_battery(inp_dict: dict[str, Any]) -> dict[str, Any]:
    """Read the battery input data
    Check the input, fill up the data with the default options
    Args:
        inp_dict (dict): input battery data field from yml file

    Returns:
        dict: complete data set for battery with default.
    """
    battery = check_input(inp_dict=inp_dict, par=_BATTERY_INPUT_)

    return battery


# ---
def check_input(inp_dict: dict[str, Any], par: dict[str, Any]) -> dict[str, Any]:
    """Check the input, and fill a new small dictionary
    of input.
    The function checks the data

    Args:
        inp_dict (dict): the data read from the configuration files
        par (dict): the global parameter dictionary on top of this file

    Raises:
        ValueError: if the parameters is not defined (i.e., it is not specified),
        but it is mandatory, throw an error and highlight at least the name of the field

    Returns:
        dict: completed dictionary with all the information for filling up the
        real input configuration.
    """
    new_dict = dict.fromkeys(par, None)
    new_dict.pop("name_field", None)

    for i in par:
        if i not in inp_dict and i != "name_field":
            # Set the default value, however, the default value are made in
            # a such way that they throw errors in case the wrong combination
            # is provided.
            if par[i][0] == "opt":
                new_dict[i] = par[i][1]
            if par[i][0] == "man":
                raise ValueError(f"{i} is a mandatory, check {par['name_field'][1]}")
        elif i in inp_dict and i != "name_field":
            new_dict[i] = inp_dict[i]

    return new_dict


# ---
def read_markets(markt: dict[str, Any]) -> dict[str, Any]:
    """Reads the market and convert path in case of flags.

    Args:
        markets (dict): check the input data of the market and release
        the post-processed one.

    Returns:
        dict: market dictionary
    """
    markets: dict[str, Any] = {}

    for i, market_config in markt.items():
        # Extract data and correct them. (From a potential incomplete input file, create
        # a dictionary that has all the option. If the mandatory data are not defined,
        # check_input generate a value Error. If the optional are not defined, it generates
        # default values. For the market, the combination of optional can generate error: i.e.,
        # you cannot have a path to a specific folder, and have packaged_true. Reason for this
        # approach: avoiding silently overwrite of user options. )
        data = check_input(inp_dict=market_config, par=_MARKET_INPUT_)
        # Set the price from the input file
        data["prices_file"] = market_config["prices_file"]

        path_to_file = None

        if data["packaged_data"] and data["path_to_file"] is None:
            path_to_file = str(
                Path(str(files("opti_market"))).resolve().parents[1] / "study_case"
            )
        elif not data["packaged_data"] and data["path_to_file"] is not None:
            path_to_file = str(Path(data["path_to_file"]))
        elif data["packaged_data"] and data["path_to_file"] is not None:
            raise ValueError(
                f"{data['path_to_file']} is a path. packaged_data must be False."
            )
        elif not data["packaged_data"] and data["path_to_file"] is None:
            raise ValueError(f"{i} does not have any path to it")

        if path_to_file is not None:
            data["path_to_file"] = path_to_file
        else:
            raise ValueError(
                "Something went wrong in this part of the code, check the options",
                "or there is an unseen bug.",
            )

        # remove the packaged information:
        data.pop("packaged_data", None)

        markets[i] = data

    return markets
# ---
def post_process_config_file(
    pre_config: dict[str, Any], config_fin: dict[str, Any]
) -> None:
    """Use the original configuration file and construct the
    effective configuration of the simulation

    Reason: Since the take-home assignment has two market, I wanted
    to flag the presence of these markets within the package, such
    that the behaviour is deterministic for the example, and also
    to inform directly the unit/integration/regression test.

    Args:
        pre_config (dict): data read from the configuration file
        config_fin (dict): final data for configure, battery and market classes
    """

    config_fin["markets"] = read_markets(pre_config["simulation"]["markets"])
    config_fin["battery"] = read_battery(pre_config["simulation"]["battery"])
    config_fin["sim_options"] = read_simulation_config(
        pre_config["simulation"]["optimization"]
    )
    config_fin['output'] = read_simulation_output(pre_config["simulation"]["output"])
    config_fin['name'] = pre_config["simulation"]["name"]

# ---
def read_configuration(config_file: str) -> dict[str, dict[str, Any]]:
    """From the config file, generate a configuration dictionary.

       The configuration dictionary contains all the relevant information
       to configure the dataclasses of the market and battery.

    Args:
        config_file (str): absolute path to the configuration file.

    Returns:
        dict: dictionary containing the information to configure the simulation
    """

    # Create the preliminary configuration file
    # -> The pre-configuration file is, then, parsed again to
    # identify the flags and substitute them with the appropriate
    # real value (e.g., if path to market == null and the packaged is true,
    # construct the path to the study_case)
    #
    configurations_sim: dict[str, dict[str, Any]] = {}
    with open(config_file, encoding="utf-8") as f:
        post_process_config_file(
            pre_config=yaml.safe_load(f), config_fin=configurations_sim
        )

    return configurations_sim
# --- 
def read_configurations_files(config_file:str)->tuple[BATTERY,
                                                 Markets,
                                                 Opti_Market_Options,
                                                 Output]:
    """Configure the simulation using the configuration file

    Args:
        config_file (str): path to the configuration file

    Returns:
        tuple[BATTERY, Markets, Opti_Market_Options, Output]: classes that handles the simulation behaviour
    """
    
    configuration_sim = read_configuration(config_file=config_file)
    
    bat = BATTERY(**configuration_sim["battery"])
    # Market
    markt = Markets(configuration_sim["markets"])
    # Solution options: {To Do: seeing the other options}
    opti_opt = Opti_Market_Options.read_optimisation_options(configuration_sim["sim_options"])
    output = Output.read_output_configuration(dict_config=configuration_sim["output"]
                                              , name_simulation=str(configuration_sim["name"]))
    
    return bat,markt,opti_opt,output
# --- 
# --- 
    
