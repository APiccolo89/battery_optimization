## Preliminary documentation: 

```
battery_optimization
├──src/ 
 ├── battery_data_base/: small database containing a json/yaml file with the battery feature
 ├── config/: submodule from the input collect the information required to run the dispach model and output the file
    ├── battery_class.py: data classes and methods related to battery. Read the information of the specific battery, fill the class and change state of the battery as a function of the cycle of charge/discharge [Historical variables]
    
    └── time_series.py: read the timeseries, compute the relevant data (median hour price, choose the interval of time for charging the battery) ? class or dictionary?

 ├── optimization: submodule containing the optimisation problem
 └── output: submodule containing the output routines (figure, csv file, H5DF)
└──test/ 
    ├── test_battery.py : check if the property of the battery are read properly 
    ├── test_optimization.py: check if the optimisation routine works 
    ├── test_output.py: check if the routine of output works. 

```
## Rule: 
1. testing below module 
2. porting into test 
3. 

