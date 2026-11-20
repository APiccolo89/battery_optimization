## Preliminary documentation: 

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
# Introduction
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

