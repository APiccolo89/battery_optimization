# Preliminary documentation: 

## Introduction
1. I used an example found in https://github.com/klostest/energy_arbitrage_work_sample/blob/master/Energy%20arbitrage.ipynb
to guide me through the problem.
2. I tried to build the design around these examples.
    → I first built the configuration module around two main dataclasses.
    → In the optimisation, I introduced either a dataclass or a typed dictionary/dictionary to handle the configuration for each day.
3. The simulation works in the following way:
in configuration.yml (base), there is a starting date and a window. The window defines how many days are covered by each optimisation.
    Given an interval:
    01/01/2018-03/01/2019
    →interval: an optimisation of prices is run every n days.

>[!NOTE]
>1. I am not accustomed to the non-linearities, so the degradation of the battery will be treated as a state updated every n days.
>2. Another simplifying assumption is that the user cannot start the simulation partway through a day, but always at 00:00 on the starting date.
>3. AI: Assistance, I used the AI to ask specific functionalities of pulp, and code revision, and provide example of usage of pulp. 


## Package layout
```
opti_market
├── base_configuration
│   ├── blue_print.yml
│   ├── double_market.yml
│   ├── single_market_a.yml
│   └── single_market_b.yml
├── conda_enviroment.yml
├── pyproject.toml
├── README.md
├── src
│   └── opti_market
│       ├── __init__.py
│       ├── __main__.py
│       ├── config_module
│       │   ├── __init__.py
│       │   ├── configuration_read.py
│       │   ├── configure_battery.py
│       │   ├── configure_market.py
│       │   ├── configure_output.py
│       │   └── configure_simulation.py
│       ├── data
│       │   └── battery_data_base.yaml
│       ├── opti_market.py
│       ├── optimisation_module
│       │   ├── __init__.py
│       │   └── optimization_routines.py
│       └── output_module
│           ├── __init__.py
│           └── write_csv_data.py
├── study_case
│   ├── convert_timeseries.py
│   ├── market_case.xlsx
│   ├── market1.csv
│   └── market2.csv
└── tests
    ├── __init__.py
    ├── configuration_folder_tests
    │   ├── double_market.yml
    │   ├── single_market_a.yml
    │   └── single_market_b.yml
    ├── test_config_battery.py
    ├── test_config_read_market.py
    ├── test_configuration.py
    └── test_optimization.py
```
## Installation

To install the package: 
```bash 
conda env create -f opti_market_enviroment.yml
```
Then:
```bash
conda activate battery_optimization
```
To run the tests:
```bash
pytest 
```
>[!NOTE]
> The tests are basic, and they refer to a specific configurations folder within the test. 
> The test has been generating while doing the package, thus they are not representative of the intended usage of the package. However, they can be used for generating scripts that use the functionalities of **opti_market**.

## Basic usage
The package has been designed to require always a configuration file. The basic templates for the task are in /base_configuration: 
- blue_print.yml: a basic reference for the configuration file
- single_market_a: optimization only for the market whose prices are defined every 0.5 Hr
- single_market_b: optimization only for the market whose prices are defined every 1.0 Hr
- double_market: optimization for both the market of the handout. 

The simplest usage is the following (in Linux/MacOS): 
```bash 
export pack_package="$PWD"

python -m opti_market --config_file "${PWD}/base_configuration/double_market.yml"

```
After the optimization, the results are stored in: 
```
results/
  └── Double_Market/
        ├── Data_Raw/
        |    ├── market_n1.csv
        |    └── market_n2.csv
        ├── Data_Window/
        |    └── window_optimisation_results.csv
        └── summary.csv
```
- Data_Raw: are the results per period of the market results (e.g.,market_n1.csv and market_n2.csv)
- Data_Window: are the results of the window of optimisation (merged for all the market): (e.g. window_optimisation_results.csv)
- summary.csv: is the summary data. 

## Configuration file 
```yaml 
simulation:
  name_dispatch: 'RandomName'
  optimization:
    window_days: 
    start_date:
    end_date: 
    max_cycles: 
    charge_min:
  battery:
    model_name: 
    degradation_model: 
    initial_cycles: 
    initial_age:
    initial_charge:
  markets:
    market1:
      prices_file: 
      path_to_file: 
      packaged_data: 
    market2:
      prices_file: 
      path_to_file: 
      packaged_data:
    outputs: 
      path_to_save: 
      basic_plot: 
      packaged_data: 
```
The design of the input configuration file is designed to run the two test cases of the task. 
The first assumptions that I made was that a battery is responsible for n market. And that a market 
is not shared by more batteries. Thus, the package is designed to single battery dispatch.
### Optimization

### Markets

### Battery
The input configuration file is composed of: 
- **name_dispatch**: The name of the simulation. 
- **battery**: The configuration option of the battery:
  - *model_name*: The name of the battery. The name of the battery is used to collect the data from the internal database (src/data/battery_data_base.yml). The only battery in the database is the one of the task ('bt001'). 
  - *degradation_model*: The degradation model of the battery. After each window of solution the battery is degraded accordingly either a linear model or a compound model. These models adjust the maximum energy of the battery as a function of the number of cycles (n) and degradation constant (a). 
    - linear: $E_{\max}(n) = E_{\max}^{0}\,\left(1 - a\,n\right)$
    - compound: $E_{\max}(n) = E_{\max}^{0}\,\left(1 - a\right)^{n}$
- **initial_cycle**: The initial cycles of the battery.
- **initial_age**: The initial age of the battery (in year). 
- **initial_charge**: The initial charge of the battery. 
>[!NOTE]
> I introduced initial age and cycle, under the assumption that a dispatch model can be re-run for on the go adjustement. For example, if the prevision of the market was not accounting for a geopolitical event (e.g., Ucranian war, Iran war), the dispatch model can be repeated from an other point of time, for making adjustment for maximising the profit with the current conditions.