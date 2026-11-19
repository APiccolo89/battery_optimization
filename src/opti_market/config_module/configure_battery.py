"""


BATTERY: Battery data class. 
BATTERY_SPEC: frozen data classes containing all the information related to the battery. Original specification of the battery. 

BATTERY_SPEC is an encapsulated frozen dataclass that contains the relative information of the choosen battery (assuming that a database of n batteries
exists). 
BATTERY: is a dataclass that contains the specification of the battery (i.e., BATTERY_SPEC), and 
"""


from dataclasses import InitVar, dataclass, field
from pathlib import Path
from typing import Literal

import numpy as np
import yaml

DegradationModel = Literal["linear", "compound"]

@dataclass(frozen=True)
class BATTERY_SPEC:
    """Class containing the information of the battery: 
    model_name:float32 :model name
    max_discharge_rate:float32 :maximum volume that can be export (MW)
    max_charge_rate:float32 :maximum volume that can be import (MW)
    max_storage_vol:float32: maximum volume storage (MWh) 
    dicharge_eff: float32: efficiency of discharge 
    charge_eff: float32: efficiency of charge
    max_cycle: int32: number of cycles of total charge/discharge of the battery
    max_life: int32: maximum year in which the battery is guarantee to have its original specification - if not used- [?]
    degradation: float32: given a number of cycle, the amount of total storage loss. 
    capex: float32: initial costs for installing the battery
    fix_cost_yr: float32: fixed cost of the battery (maintainance...)
    cur_cycle: int32: current cycle 
    cur_age: int2: current age 
    """
    
    model_name:str
    max_discharge_rate: float
    max_charge_rate: float 
    max_storage_vol: float
    charge_eff: float 
    discharge_eff: float
    max_cycle: float
    max_life: int
    degradation: float
    capex: float
    fix_cost_yr: float 
    currency:str 
# ---
@dataclass
class BATTERY:
    model_name: InitVar[str]
    battery_spec:BATTERY_SPEC = field(init=False)
    # Initial state of the battery
    # --- 
    # I don't know if the battery is new, or it has been used. I assume by default that it is new. 
    # But I imagine that as a function of the political situation, it may necessary to repeat the 
    # the simulation for a given point of time, using the current state of the battery and readjusting 
    # parameters. For example, at the moment I do not know, sincerely, if there are additional 
    # configurations of the network that can be informed by the software for adjusting on the go 
    # the charge/discharge. Given this ignorance, I let open this possibility. 
    # --- 
    initial_charge: float = 0.5
    initial_cycles: float = 0
    initial_age: int = 0 
    # Current state variable
    effective_max_storage_vol : float = 0.0
    total_number_cycle : float = 0.0 
    cumulative_power_discharged : float = 0.0
    degradation_model : DegradationModel = 'linear'
    # TO DECIDE - as soon as I set up the optimisation solver 
    # current_charge
    # define the concept of cycles
    # --- 
    def __post_init__(self
                      ,model_name:str)->None:
        """Update the battery_spec
        Read the yml file containing the battery specification 
        Fill the battery_spec sub-class 

        Args:
            mname (str): _description_
        """
        self.read_yml_battery(model_name)
        # Update the initial state. 
        self.total_number_cycle = self.initial_cycles
        self._update_effective_max_storage_vol()
        if self.total_number_cycle >0: 
            self.cumulative_power_discharged = self.analytical_total_discharge()
        elif self.total_number_cycle<0: 
            raise ValueError('The number of cycle must be positive, check the'
                             'the initial number of cycle input')
        
    # --- 
    def read_yml_battery(self,mname:str)->None:
        """Read the yaml file containing the batteries information
        
        Args:
            mname (str): model name. battery model name. 

        Raises:
            ValueError: f'{mname} is not in the database',
                             f'avaiable batteries: {sorted(batteries)}'
        """
        
        path = Path(__file__).resolve().parents[1] / 'data' / 'battery_data_base.yaml'
        with open(path, encoding="utf-8") as f:
            batteries = yaml.safe_load(f)
        
        if mname not in batteries:
            raise ValueError(f'{mname} is not in the database',
                             f'avaiable batteries: {sorted(batteries)}')
        
        self.battery_spec = BATTERY_SPEC(**batteries[mname])
    # --- 
    def get_spec_battery(self,spec:str):
        """Function that reads the specification of the battery

        Args:
            spec (str): name of the specification

        Returns:
            Any: specification value. 
        """
        
        return getattr(self.battery_spec,spec)
    # --- 
    def _update_total_discharge(self,dE:float)->None:
        """Update the total discharge 
        dE: total discharge for a given amount of time (i.e., sold energy to the market)
        Update the energy discharge
        """ 
        
        if dE > 0: 
            raise ValueError('The energy must be negative')
        
        self.cumulative_power_discharged = self.cumulative_power_discharged \
            + np.abs(dE) 
    # --- 
    def analytical_total_discharge(self)->float:
        """Compute the analytical total discharge. 
        The analytical expression for the total energy can be derived
        by a simple integration of the total number of cycle.
        """
        E0 = self.get_spec_battery('max_storage_vol')
        degradation = self.get_spec_battery('degradation')/100
        n = self.total_number_cycle 
        if self.degradation_model == 'compound':
            E_anal = (self.effective_max_storage_vol - E0) / np.log(1 - degradation)
        elif self.degradation_model == 'linear':
            E_anal = E0 * (n - degradation * n**2 / 2)
        else: 
            raise ValueError('Wrong degradation model')

        return E_anal
    # --- 
    def _update_effective_max_storage_vol(self)->None:
        """Update the effective max storage volume using 
        a compound forumation or a linear formulation. 
        TO DO: pyfile of global configuration to modify, or introducing
        directly the option in the class battery
        """
        if self.degradation_model == 'compound':
            self.effective_max_storage_vol = self.get_spec_battery('max_storage_vol') * \
                (1-self.get_spec_battery('degradation')/100)**self.total_number_cycle
        if self.degradation_model == 'linear':
            self.effective_max_storage_vol = self.get_spec_battery('max_storage_vol') * \
                (1-self.get_spec_battery('degradation')/100 *self.total_number_cycle)
    # --- 
    def _update_cycle(self,dE:float)->None:
        """Update the number of cycle using the current discharge 
        and using the previous effective_max_volume. 

        Args:
            dE (float): currenty energy
        """

        self.total_number_cycle = self.total_number_cycle \
            + np.abs(dE)/self.effective_max_storage_vol
    # --- 
    def update_state_battery(self,dE:float)->None:
        if dE > 0: 
            raise ValueError('The total discharge must be always negative')
        else: 
            self._update_cycle(dE)
            self._update_effective_max_storage_vol()
            self._update_total_discharge(dE)
