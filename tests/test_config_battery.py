import numpy as np
import pytest

from opti_market.config_module import BATTERY
# --- 
# --- 
def test_specification_battery(mname:str = 'bt001'):
    bat = BATTERY(model_name=mname)
    assert np.isclose(bat.get_spec_battery('max_discharge_rate'),2.0,rtol=1e-2) 
    assert np.isclose(bat.get_spec_battery('max_charge_rate'),2.0,rtol=1e-2)
    assert np.isclose(bat.get_spec_battery('capex'),500000,rtol=1e-2)
# --- 
def test_read_battery(): 
    # Read the battery and check wheter or not the name, and the other data are there. 
    try: 
        bat = BATTERY(model_name = 'bt001')
        passed = True 
    except Exception: 
        # TO BE DONE: class of error to classify the several instance and potential errors
        # For now, the basic test is: do the class read the only battery introduced in the 
        # data? Y/N
        passed = False
        
    assert passed 
# ---
def test_used_battery_cumulative_discharge():
    """Test the analytical formulation for the total discharge. 
    """
    b = BATTERY(model_name="bt001", initial_cycles=400)
    assert np.isclose(b.effective_max_storage_vol,3.984, rtol=1e-4)
    assert np.isclose(b.cumulative_power_discharged,1596.8, rtol=1e-3)
