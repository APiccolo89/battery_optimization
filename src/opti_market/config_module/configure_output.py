from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path
from typing import Any


# ---
# ---
@dataclass(frozen=True)
class Output:
    path_to_save: Path
    basic_plot: bool
    # --- 
    @staticmethod
    def prepare(path:Path) -> Path:
        """Create the output folder if needed and return it."""
        path.mkdir(parents=True, exist_ok=True)
    # --- 
    @classmethod
    def read_output_configuration(cls, dict_config: dict[str, Any], name_simulation: str) -> "Output":
        """Build the output settings from the 'output' section of the configuration."""
        if dict_config["default_location"]:
            base = Path(str(files("opti_market"))).resolve().parents[1]
        else:
            base = Path(dict_config["path_to_save"])
        path = base / 'results' / name_simulation
        
        cls.prepare(path)
        
        return cls(path_to_save=path,
                   basic_plot=dict_config["basic_plot"])