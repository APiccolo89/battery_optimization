"""Output settings: results folder and output options."""

from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path
from typing import Any


# ---
# ---
@dataclass(frozen=True)
class Output:
    """Output settings of the simulation.

    Attributes:
        path_to_save (Path): folder where the results are written.
        basic_plot (bool): plot flag read from the configuration; not used
            elsewhere in the package.
        clean_option (bool): if True, an existing results folder is removed
            before the run.
    """
    path_to_save: Path
    basic_plot: bool
    clean_option: bool

    # ---
    @staticmethod
    def prepare(path: Path) -> None:
        """Create the output folder if needed and return it."""
        path.mkdir(parents=True, exist_ok=True)

    # ---
    @classmethod
    def read_output_configuration(
        cls, dict_config: dict[str, Any], name_simulation: str
    ) -> "Output":
        """Build the output settings from the 'output' section of the configuration."""
        if dict_config["default_location"]:
            base = Path(str(files("opti_market"))).resolve().parents[1]
        else:
            base = Path(dict_config["path_to_save"])
        path = base / "results" / name_simulation

        cls.prepare(path)

        return cls(
            path_to_save=path,
            basic_plot=dict_config["basic_plot"],
            clean_option=dict_config["clean_option"],
        )
