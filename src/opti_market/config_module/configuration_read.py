"""
Definition of options for the input configuration file. 

'man':'mandatory', => If it is not defined, the program is preventevely blocked
'opt': 'fully optional, if anything is defined, the default value are applied' 
"""

from importlib.resources import files
from pathlib import Path

import yaml

# --- 
# The lowest level of the dictionary always
_BATTERY_INPUT_ = {'model_name': ('man',None),
                   'degradation_model':('opt','linear'),
                   'initial_cycle':('opt',0),
                   'initial_age':('opt',0),
                   'name_field': ('battery')}

_MARKET_INPUT_ = {'prices_file' : ('man',None),
                  'path_to_file': ('opt',None),
                  'packaged_data': ('opt',True),
                  'name_field':('market')}


# --- 
# --- 
def read_battery(inp_dict:dict)->dict:
    """Read the battery input data
    Check the input, fill up the data with the default options
    Args:
        inp_dict (dict): input battery data field from yml file

    Returns:
        dict: complete data set for battery with default. 
    """
    battery = check_input(inp_dict=inp_dict,par=_BATTERY_INPUT_)
    
    return battery 
# --- 
def check_input(inp_dict:dict,par:dict)-> dict: 
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
    new_dict.pop('name_field',None)

    for i in par:
        if i not in inp_dict and i != 'name_field':  # noqa: SIM102
            # Set the default value, however, the default value are made in 
            # a such way that they throw errors in case the wrong combination
            # is provided. 
            if par[i][0] == 'opt':
                new_dict[i] = par[i][1]
            if par[i][0] == 'man':
                raise ValueError(f"{i} is a mandatory, check {par['name_field']}")
        elif i in inp_dict and i != 'name_field':
            new_dict[i] = inp_dict[i]
    
    return new_dict
                
# --- 
def read_markets(markt:dict)->dict:
    """Reads the market and convert path in case of flags. 

    Args:
        markets (dict): check the input data of the market and release 
        the post-processed one.

    Returns:
        dict: market dictionary
    """    
    markets = {}
    for i in markt:
        data = check_input(inp_dict = markt[i], par = _MARKET_INPUT_)
        data['prices_file'] = markt[i]['prices_file']
        if data['packaged_data'] and data['path_to_file'] is None:
            path_to_file = Path(files("opti_market")).resolve().parents[1] / 'study_case'
        elif not data['packaged_data'] and data['path_to_file'] is not None:
            path_to_file = Path(data['path_to_file'])
        elif data['packaged_data'] and data['path_to_file'] is not None:
            raise ValueError(f"{data['path_to_file']} is a path. packaged_data must be False.")
        elif not data['packaged_data'] and data['path_to_file'] is None:
            raise ValueError(f'{i} does not have any path to it')
        
        data['path_to_file'] = path_to_file
        # remove the packaged information: 
        data.pop('packaged_data', None)
        
        markets[i] = data

    return markets 
# --- 
def post_process_config_file(pre_config:dict,config_fin:dict)->None:
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
    

    config_fin['markets'] = read_markets(pre_config['simulation']['markets'])
    config_fin['battery'] = read_battery(pre_config['simulation']['battery'])
    
# --- 
def read_configuration(config_file:str)->dict:
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
    configurations_sim ={}
    with open(config_file, encoding="utf-8") as f:
        post_process_config_file(pre_config=yaml.safe_load(f),config_fin=configurations_sim)
    
    return configurations_sim 


    


if __name__ == '__main__':
    
    pass 
