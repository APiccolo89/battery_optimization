"""Battery specification and battery state during the simulation."""

from dataclasses import InitVar, dataclass, field
from pathlib import Path
from typing import Literal

import numpy as np
import yaml

DegradationModel = Literal["linear", "compound","none"]


@dataclass(frozen=True)
class BATTERY_SPEC:
    """Class containing the information of the battery:
    model_name:str :model name
    max_discharge_rate:float32 :maximum volume that can be exported (MW)
    max_charge_rate:float32 :maximum volume that can be imported (MW)
    max_storage_vol:float32: maximum storage volume (MWh)
    discharge_eff: float32: efficiency of discharge
    charge_eff: float32: efficiency of charge
    max_cycle: int32: number of cycles of total charge/discharge of the battery
    max_life: int32: maximum year in which the battery is guaranteed to have its original specification - if not used - [?]
    degradation: float32: given a number of cycles, the amount of total storage loss.
    capex: float32: initial costs for installing the battery
    fix_cost_yr: float32: fixed cost of the battery (maintenance...)
    cur_cycle: int32: current cycle
    cur_age: int2: current age
    """

    model_name: str
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
    currency: str


# ---
@dataclass
class BATTERY:
    """Battery model and its state during the simulation.

    The specification is read from the battery database (battery_data_base.yaml)
    using model_name. The state (number of cycles, effective storage volume and
    cumulative discharged energy) is updated after each optimisation window.

    Attributes:
        model_name (str): name of the battery model in the database (init only).
        battery_spec (BATTERY_SPEC): specification of the battery model.
        initial_charge (float): initial stored energy, as a fraction of the
            effective maximum storage volume.
        initial_cycles (float): number of cycles already performed by the battery.
        initial_age (int): initial age of the battery.
        effective_max_storage_vol (float): current maximum storage volume after
            degradation (MWh).
        total_number_cycle (float): current number of cycles.
        cumulative_power_discharged (float): cumulative discharged energy (MWh).
        degradation_model (str): "linear", "compound" or "none".
    """
    model_name: InitVar[str]
    battery_spec: BATTERY_SPEC = field(init=False)
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
    effective_max_storage_vol: float = 0.0
    total_number_cycle: float = 0.0
    cumulative_power_discharged: float = 0.0
    degradation_model: DegradationModel = "linear"

    # TO DECIDE - as soon as I set up the optimisation solver
    # current_charge
    # define the concept of cycles
    # ---
    def __post_init__(self, model_name: str) -> None:
        """Update the battery_spec.
        Read the yml file containing the battery specification.
        Fill the battery_spec sub-class.

        Args:
            mname (str): _description_
        """
        self.read_yml_battery(model_name)
        # Update the initial state.
        self.total_number_cycle = self.initial_cycles
        self._update_effective_max_storage_vol()
        if self.total_number_cycle > 0:
            self.cumulative_power_discharged = self.analytical_total_discharge()
        elif self.total_number_cycle < 0:
            raise ValueError(
                "The number of cycle must be positive, check the"
                "the initial number of cycle input"
            )

    # ---
    def read_yml_battery(self, mname: str) -> None:
        """Read the yaml file containing the battery information.

        Args:
            mname (str): model name. battery model name.

        Raises:
            ValueError: f'{mname} is not in the database',
                             f'avaiable batteries: {sorted(batteries)}'
        """

        path = Path(__file__).resolve().parents[1] / "data" / "battery_data_base.yaml"
        with open(path, encoding="utf-8") as f:
            batteries = yaml.safe_load(f)

        if mname not in batteries:
            raise ValueError(
                f"{mname} is not in the database",
                f"avaiable batteries: {sorted(batteries)}",
            )

        self.battery_spec = BATTERY_SPEC(**batteries[mname])

    # ---
    def get_spec_battery(self, spec: str):
        """Function that reads the specification of the battery

        Args:
            spec (str): name of the specification

        Returns:
            Any: specification value.
        """

        return getattr(self.battery_spec, spec)

    # ---
    def _update_total_discharge(self, dE: float) -> None:
        """Update the total discharge.
        dE: total discharge for a given amount of time (i.e., energy sold to the market).
        Update the energy discharge.
        """

        if dE > 0:
            raise ValueError("The energy must be negative")

        self.cumulative_power_discharged = self.cumulative_power_discharged + np.abs(dE)

    # ---
    def analytical_total_discharge(self) -> float:
        """Compute the analytical total discharge.
        The analytical expression for the total energy can be derived
        by a simple integration of the total number of cycles.
        """
        E0 = self.get_spec_battery("max_storage_vol")
        degradation = self.get_spec_battery("degradation") / 100
        n = self.total_number_cycle
        if self.degradation_model == "compound":
            E_anal = (self.effective_max_storage_vol - E0) / np.log(1 - degradation)
        elif self.degradation_model == "linear":
            E_anal = E0 * (n - degradation * n**2 / 2)
        elif self.degradation_model == "none":
            E_anal = E0 * n
        else:
            raise ValueError("Wrong degradation model")

        return E_anal

    # ---
    def _update_effective_max_storage_vol(self) -> None:
        """Update the effective max storage volume using
        a compound formulation or a linear formulation.
        TO DO: pyfile of global configuration to modify, or introducing
        directly the option in the class battery
        """
        if self.degradation_model == "compound":
            self.effective_max_storage_vol = (
                self.get_spec_battery("max_storage_vol")
                * (1 - self.get_spec_battery("degradation") / 100)
                ** self.total_number_cycle
            )
        if self.degradation_model == "linear":
            self.effective_max_storage_vol = self.get_spec_battery(
                "max_storage_vol"
            ) * (
                1 - self.get_spec_battery("degradation") / 100 * self.total_number_cycle
            )
        if self.degradation_model == "none":
            self.effective_max_storage_vol = self.get_spec_battery("max_storage_vol")

    # ---
    def _update_cycle(self, dE: float) -> None:
        """Update the number of cycles using the current discharge
        and using the previous effective_max_volume.

        Args:
            dE (float): current energy
        """

        self.total_number_cycle = (
            self.total_number_cycle + np.abs(dE) / self.effective_max_storage_vol
        )

    # ---
    def update_state_battery(self, dE: float) -> None:
        """Update the battery state after a discharge.

        Update the number of cycles, the effective maximum storage volume and
        the cumulative discharged energy, in this order.

        Args:
            dE (float): discharged energy (MWh), as a non-positive value.

        Raises:
            ValueError: if dE is positive.
        """
        if dE > 0:
            raise ValueError("The total discharge must be always negative")
        else:
            self._update_cycle(dE)
            self._update_effective_max_storage_vol()
            self._update_total_discharge(dE)
