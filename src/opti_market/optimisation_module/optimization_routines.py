import numpy as np
import pandas as pd
import pulp


# From an initialised problem, add problem (i.e., add markets)
def add_market():
    
    pass 

# Read the constraints and introduce them into the problem 
def read_constraints():
    
    pass
# Entry point
def configure_problem():
    
    prob = pulp.LpProblem(name_problem, pulp.LpMaximize)
    charging = prob.add_variables_dicts('charging',)
    
    pass

# Solve the problem
def solve_problem():

    pass 

# Produce the final output
def produce_output():
    
    pass

# Test used to introduce the optimisation: function during the development.
# -> getting knowing the variable and how to do the configuration 
# -> 
def test_integration_test():
    from opti_market.config_module import BATTERY, read_market
    from importlib.resources import files

    path = Path(files("opti_market")).resolve().parents[1] / 'study_case'

    bat = BATTERY(mname='bt001')
    market1 = read_market(market1,path)
    

if __name__ == '__main__':
    
    test_integration_test()