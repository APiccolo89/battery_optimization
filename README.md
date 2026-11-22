# Preliminary documentation: 
## Package layout
```
opti_market
├── base_configuration
│   ├── double_market.yml
│   └── single_market.yml
├── src
│   └── opti_market
│       ├── config_module
│       │   ├── __init__.py
│       │   ├── configuration_read.py
│       │   ├── configure_battery.py
│       │   └── configure_market.py
│       ├── data
│       │   └── battery_data_base.yaml
│       ├── optimisation_module
│       │   ├── __init__.py
│       │   ├── design_note.md
│       │   └── optimization_routines.py
│       ├── utils_module
│       └── __init__.py
├── study_case
│   ├── convert_timeseries.py
│   ├── market_case.xlsx
│   ├── market1.csv
│   └── market2.csv
├── tests
│   ├── __init__.py
│   ├── test_config_battery.py
│   ├── test_config_read_market.py
│   └── test_configuration.py
├── conda_enviroment.yml
├── pyproject.toml
└── README.md
```
## Installation

## Basic usage


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