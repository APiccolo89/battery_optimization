# Preliminary documentation

## Introduction
The problem that **opti_market** solves is to optimize the charge and discharge of a battery connected to 1 or 2 markets, such that the profit is the maximum possible, considering the degradation of the battery and other constraints that preserve the state of the battery, with the additional binary constraint to not have a battery that charges and discharges at the same time. The package that has been chosen to solve the optimization is [PuLP](https://github.com/coin-or/pulp), and the corresponding solver is [HiGHS](https://highs.dev); both are free and easy to install with *conda* or *pip*. These packages are easy to use, and there is a wide variety of usage examples. Since the problem requires that the battery is not charging while discharging, it is necessary to use a package that is able to configure an optimization problem with both continuous and integer variables (i.e., charge or discharge), so HiGHS was the best choice. The optimization maximizes the profit as a function of a given interval of time (in days). So, if the user ran a simulation of one year, with a time interval of 1 day, the final results would be the results of 365 optimizations. The package reads the markets in `.csv` format, collects the information of the markets, and computes the minimal time resolution to use in the optimization routine. The package stores all the prices of the markets redundantly. The battery specification is read from an internal database. The internal database contains all the specifications of the batteries, and, using this information, the package constructs the battery that is dispatched for the given markets. The battery can degrade, and there are three models of degradation: `linear` (which assumes that the degradation always refers to the initial state), `compound` (which assumes that the degradation refers to the previous state) and `none` (which assumes no degradation model). The package requires a configuration file that contains the information of the simulation (where to find the markets, which battery to use, and where to save the data). This configuration file contains additional constraints for the optimization: the minimal energy that the dispatched battery should retain at the end of the simulation, the time frame to perform the optimization, and the window of optimization (i.e., the number of days of each optimization). The package releases the output of a given simulation as a series of `.csv` files. The package has not been designed yet to provide a graphical representation of the extracted data. 


>[!WARNING]
> The package is designed to accept several models of degradation. However, the degradation introduces non-linearities. Since the package updates the battery state after each optimization window, the degradation models should be used with extra care regarding the window of optimization. For example, if the optimization is unconstrained, in principle the user can use the entire year as the optimization window. However, if the user wants to quantify the battery degradation, they should use a reasonable window. The basic deployment of the battery in this package always assumes a 1-day optimization window.

>[!NOTE]
> The linear degradation formulation can be linearised and introduced natively within the linear optimization packaged. However, I preferred to have only one formulation and not introduce cases/subcases. 




>[!NOTE]
>1. I am not accustomed to non-linearities, so the degradation of the battery is treated as a state updated every n days.
>2. Another simplifying assumption is that the user cannot start the simulation partway through a day, but always at 00:00 on the starting date.
>3. AI assistance: I used AI to ask about specific functionalities of PuLP, for code revision, and to provide examples of PuLP usage and a few functionalities concerning the pd.Dataframe (used as a flexible stackoverflow)


## Package layout
```
opti_market
├── base_configuration
│   ├── blue_print.yml
│   ├── double_market_min_charge.yml 
│   ├── double_market_unconstrained.yml #
│   ├── double_market.yml
│   ├── single_market_a.yml
│   └── single_market_b.yml
├── opti_market_enviroment.yml
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
| `effective_max_pow_mw` | MWh | Storage capacity at the end of the simulation, after degradation (initially `max_storage_vol`, 4 MWh for bt001). |

## Three template final results

The basic examples yield the following results:
| | Market 1 only | Market 2 only | Both markets | Both markets, 25% minimum charge | Both markets, no constraints, no degradation |
|---|---:|---:|---:|---:|---:|
| Configuration file | single_market_a.yml | single_market_b.yml | double_market.yml | double_market_min_charge.yml | double_market_unconstrained.yml |
| Period | 2018-01-01 – 2019-01-07 | 2018-01-01 – 2019-01-07 | 2018-01-01 – 2019-01-07 | 2018-01-01 – 2019-01-07 | 2018-01-01 – 2019-01-07 |
| Days simulated | 372 | 372 | 372 | 372 | 372 |
| Degradation model | linear | linear | linear | linear | none |
| Maximum cycles per day | 1.37 | 1.37 | 1.37 | 1.37 | no limit |
| Minimum charge | 0% | 0% | 0% | 25% | 0% |
| **Total revenue** | £46,087.76 | £53,076.35 | £58,527.53 | £50,240.62 | £67,958.35 |
| Revenue per day | £123.89 | £142.68 | £157.33 | £135.06 | £182.68 |
| Net revenue, Market 1 | £46,087.76 | – | −£54,221.22 | −£47,408.89 | −£109,745.39 |
| Net revenue, Market 2 | – | £53,076.35 | £112,748.75 | £97,649.50 | £177,703.73 |
| Battery cycles | 491.59 | 493.36 | 508.24 | 504.72 | 950.37 |
| Cycles per day | 1.32 | 1.33 | 1.37 | 1.36 | 2.55 |
| Capacity at the end | 3.98 MWh | 3.98 MWh | 3.98 MWh | 3.98 MWh | 4.00 MWh |
| Energy at the end | 0.00 MWh | 0.00 MWh | 0.00 MWh | 0.99 MWh | 0.00 MWh |

## Configuration file

Every simulation is defined by one YAML file. `base_configuration/blue_print.yml` is an empty template:

```yaml
simulation:
  name: 'Random_name'
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
  output:
    path_to_save:
    default_location:
    clean_option:
```

Fields marked as optional can be omitted: the default value is then used. A missing mandatory field stops the program with an error that names the field.

### simulation

| Key | Required | Default | Description |
|---|---|---|---|
| `name` | yes | – | Name of the simulation. It is also the name of the output folder (`results/<name>`). |

### optimization

| Key | Required | Default | Description |
|---|---|---|---|
| `start_date` | yes | – | First day of the simulation (`YYYY/MM/DD` or `YYYY-MM-DD`). The simulation always starts at 00:00. |
| `end_date` | no | `start_date` + 1 day | End of the simulation, **excluded**. With `end_date: 2019/01/08`, the last simulated day is 2019-01-07. |
| `window_days` | no | 1 | Length of each optimisation window in days. The number of days between `start_date` and `end_date` must be a multiple of `window_days`. |
| `max_cycles` | no | 1e9 (no limit) | Maximum equivalent full cycles per optimisation window: the energy drawn from the battery in a window cannot exceed `max_cycles` × current capacity. The base configurations use 1.37 = 5000 cycles / 10 years / 365 days. |
| `charge_min` | no | 0.0 | Minimum energy kept in the battery, as a fraction (0–1) of the current capacity. It must not be larger than `initial_charge`, otherwise the first window has no solution. |

### battery

| Key | Required | Default | Description |
|---|---|---|---|
| `model_name` | yes | – | Name of the battery in `src/opti_market/data/battery_data_base.yaml`. The database contains only the battery of the task (`bt001`). |
| `degradation_model` | no | `linear` | `linear`, `compound` and `none`. After each window, the storage capacity is updated from the number of cycles *n* and the degradation per cycle *a*: linear $E_{\max}(n) = E_{\max}^{0}(1 - a\,n)$, compound $E_{\max}(n) = E_{\max}^{0}(1 - a)^{n}$. None, instead is not applying any degradation model|
| `initial_cycles` | no | 0 | Equivalent full cycles already done by the battery before the simulation. The initial capacity is degraded accordingly. |
| `initial_age` | no | 0 | Age of the battery in years. Stored, but not used in the current version. |
| `initial_charge` | no | 0.5 | Energy in the battery at the start of the simulation, as a fraction (0–1) of the capacity. |

### markets

One block per market (`market1`, `market2`, …; at most 6). The names are free; the markets are numbered `market_n1`, `market_n2`, … in the order they appear, and these numbers are used in the output files.

| Key | Required | Default | Description |
|---|---|---|---|
| `prices_file` | yes | – | Name of the CSV file with the prices. Columns: `timestamp`, `price_gbp_per_mwh`. The time step must be 15, 30, 45 or 60 minutes and constant. |
| `packaged_data` | no | True | If True, the file is read from the `study_case` folder of the repository. |
| `path_to_file` | no | null | Folder containing `prices_file`. Use it with `packaged_data: False`. Setting both a path and `packaged_data: True` is an error. |

### output

| Key | Required | Default | Description |
|---|---|---|---|
| `default_location` | no | True | If True, the results are saved in `<repository>/results/<name>`. |
| `path_to_save` | no | null | Folder where the results are saved (`<path_to_save>/results/<name>`). Use it with `default_location: False`. |
| `clean_option` | no | True | If the output folder already exists, True deletes it and writes the new results; False stops the program. |

### Example

The configuration of the double-market case (`base_configuration/double_market.yml`):

```yaml
simulation:
  name: Double_Market
  optimization:
    window_days: 1
    start_date: 2018/01/01
    end_date: 2019/01/08
    max_cycles: 1.37
    charge_min: 0.0
  battery:
    model_name: bt001
    degradation_model: linear
    initial_cycles: 0
    initial_age: 0
    initial_charge: 0.5
  markets:
    market1:
      prices_file: market1.csv
      path_to_file: null
      packaged_data: True
    market2:
      prices_file: market2.csv
      path_to_file: null
      packaged_data: True
  output:
    path_to_save: null
    default_location: True
    clean_option: True
```
