import argparse
import shutil
from pathlib import Path

from opti_market.config_module import (
    read_configurations_files,
)
from opti_market.optimisation_module import solve_problem


# function to run the function
def run_opti_market(args: list[str]|None = None):
    # Parse the arguments
    parser = argparse.ArgumentParser(
        prog="python -m opti_market",
        description="Optimise battery dispatch across electricity markets.",
        epilog=(
            "examples:\n"
            "  basic examples: python -m opti_market path_to_package/base_configuration/double_market.yml\n"
            "        examples: python -m opti_market configuration_path/name_configuration.yml\n"
            "  The package can refer to the basic configuration files within the package or any arbitrary location.\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--config_file",required=True, type=str, help="path to the YAML configuration file")
    parsed_args = parser.parse_args(args)

    # If no configuration path has been provided, throw an error
    if not Path(parsed_args.config_file).is_file():
        raise ValueError('The configuration file path is wrong, or the file does not exist')
    # Read the configuration and collect the classes
    print(f'1. Configure the simulation using {parsed_args.config_file}')
    bat,markt,opti_option,output = read_configurations_files(parsed_args.config_file)
    if output.path_to_save.is_dir() and output.clean_option:
        print('The old test is removed, to substitute with the new results')
        shutil.rmtree(output.path_to_save, ignore_errors=True)
    elif output.path_to_save.is_dir() and not output.clean_option:
        raise ValueError('The path of the folder is existing: change the name of the simulation or activate clean_option.')
    
    # Run the optimization files
    print('2. Running the simulation ... ')
    print(f'                         output are saved in {output.path_to_save} ')
    solve_problem(bat=bat,
                  markt=markt,
                  opti_opt=opti_option,
                  output=output)
    print('3. Simulation end ')

if __name__ == '__main__':
    run_opti_market()

    
    
    

    
    

