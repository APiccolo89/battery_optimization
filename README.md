# Preliminary documentation

## Introduction
The main challanges was related to the undestanding of the problem and how to solve it. 

>[!NOTE]
>1. I am not accustomed to non-linearities, so the degradation of the battery is treated as a state updated every n days.
>2. Another simplifying assumption is that the user cannot start the simulation partway through a day, but always at 00:00 on the starting date.
>3. AI assistance: I used AI to ask about specific functionalities of PuLP, for code revision, and to provide examples of PuLP usage and a few functionalities concerning the pd.Dataframe (used as a flexible stackoverflow)


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
> The tests are basic, and they refer to a specific configuration folder within the tests folder.
> The tests were generated while developing the package; thus, they are not representative of the intended usage of the package. However, they can be used for generating scripts that use the functionalities of **opti_market**.

## Basic usage
The package has been designed to always require a configuration file. The basic templates for the task are in /base_configuration:
- blue_print.yml: a basic reference for the configuration file
- single_market_a: optimisation only for the market whose prices are defined every 0.5 h
- single_market_b: optimisation only for the market whose prices are defined every 1.0 h
- double_market: optimisation for both markets of the handout.

The simplest usage is the following (in Linux/macOS):
```bash
export pack_package="$PWD"

python -m opti_market --config_file "${PWD}/base_configuration/double_market.yml"

```
After the optimisation, the results are stored in:
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
- Data_Raw: contains the results of each market, per period (e.g., market_n1.csv and market_n2.csv).
- Data_Window: contains the results of each optimisation window (merged for all the markets) (e.g., window_optimisation_results.csv).
- summary.csv: contains the summary data.
### Data_Raw csv format:

| Column | Unit | Definition |
|---|---|---|
| `timestamp` | date and time | Start of the market period. Each row covers one period of the market's own resolution (30 minutes for Market 1, 1 hour for Market 2). |
| `price_gbp_per_mwh` | £/MWh | Market price for that period, from the input data. |
| `charge_mw` | MW | Power bought from this market during the period, i.e. energy flowing from the grid into the battery. Constant over the whole period (commitment rule). |
| `discharge_mw` | MW | Power sold to this market during the period, i.e. energy flowing from the battery to the grid. Constant over the whole period. |
| `revenue_gbp` | £ | Net cash flow of the period: price × (discharge − charge) × period length in hours. Negative when the battery buys, positive when it sells. |
### Data_Window csv format:
| Column | Unit | Definition |
|---|---|---|
| `start` | date and time | Start of the optimisation window (included), always at 00:00. |
| `end` | date and time | End of the window (excluded): `start` + window length. |
| `total_revenue_gbp` | £ | Profit of the window: the sum of the net revenues of all markets over the window. |
| `energy_end_mwh` | MWh | Energy stored in the battery at the end of the window. It becomes the starting energy of the next window. |
| `discharged_mwh` | MWh | Energy drawn from the battery during the window, including discharge losses: the sum of all decreases of the stored energy. It drives the cycle count and the degradation update. |

### Summary
| Metric | Unit | Definition |
|---|---|---|
| `start_date` | date | First moment of the simulation (included), at 00:00. |
| `end_date` | date | End of the simulation (**excluded**): the last simulated window ends just before this moment. With `end_date` = 2019-01-02, the last simulated day is 2019-01-01. |
| `optimization_window` | days | Length of each optimisation window. Each window is solved separately, and the battery state is carried over to the next one. |
| `battery_model` | – | Name of the battery in the battery database (`battery_data_base.yaml`). |
| `total_revenue` | GBP | Total profit over the simulation: the sum of the net revenues of all markets and all windows. |
| `final_energy_mwh` | MWh | Energy stored in the battery at the end of the last window. |
| `market_revenues:<market>` | GBP | Net revenue of each market over the whole simulation. Negative when the battery mainly buys in that market. The market values add up to `total_revenue`. |
| `battery_cyles` | cycles | Equivalent full cycles at the end of the simulation, including any `initial_cycles` of the battery. One cycle = discharging the full storage capacity; partial discharges add up. |
| `total_energy_left_mwh` | MWh | Energy left in the battery at the end of the simulation. |
| `effective_max_pow_mw` | MWh | Storage capacity at the end of the simulation, after degradation (initially `max_storage_vol`, 4 MWh for bt001). |

## Three template final results

The basic examples yield the following results:

| | Market 1 only | Market 2 only | Both markets |
|---|---:|---:|---:|
| Period | 2018-01-01 – 2019-01-07 | 2018-01-01 – 2019-01-07 | 2018-01-01 – 2019-01-07 |
| Days simulated | 372 | 372 | 372 |
| **Total revenue** | £46,087.76 | £53,076.35 | £58,527.53 |
| Revenue per day | £123.89 | £142.68 | £157.33 |
| Net revenue, Market 1 | £46,087.76 | – | −£54,221.22 |
| Net revenue, Market 2 | – | £53,076.35 | £112,748.75 |
| Battery cycles | 491.59 | 493.36 | 508.24 |
| Cycles per day | 1.32 | 1.33 | 1.37 |
| Capacity at the end | 3.98 MWh | 3.98 MWh | 3.98 MWh |

>[!NOTE]
> To run each of the cases above, use the following configuration files:
> Market 1 only: single_market_a.yml
> Market 2 only: single_market_b.yml
> Both markets: double_market.yml

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
      clean_data:
```
The input configuration file is designed to run the two test cases of the task.
The first assumption that I made was that a battery is responsible for n markets, and that a market
is not shared by more than one battery. Thus, the package is designed for single-battery dispatch.
### Optimization

### Markets

### Battery
The input configuration file is composed of:
- **name_dispatch**: The name of the simulation.
- **battery**: The configuration options of the battery:
  - *model_name*: The name of the battery. The name of the battery is used to collect the data from the internal database (src/data/battery_data_base.yml). The only battery in the database is the one from the task ('bt001').
  - *degradation_model*: The degradation model of the battery. After each window of solution, the battery is degraded according to either a linear model or a compound model. These models adjust the maximum energy of the battery as a function of the number of cycles (n) and the degradation constant (a).
    - linear: $E_{\max}(n) = E_{\max}^{0}\,\left(1 - a\,n\right)$
    - compound: $E_{\max}(n) = E_{\max}^{0}\,\left(1 - a\right)^{n}$
- **initial_cycle**: The initial number of cycles of the battery.
- **initial_age**: The initial age of the battery (in years).
- **initial_charge**: The initial charge of the battery.
>[!NOTE]
> I introduced the initial age and cycles under the assumption that a dispatch model can be re-run for on-the-go adjustments. For example, if the market forecast did not account for a geopolitical event (e.g., the Ukrainian war, the Iran war), the dispatch model can be repeated from another point in time to make adjustments that maximise the profit under the current conditions.
