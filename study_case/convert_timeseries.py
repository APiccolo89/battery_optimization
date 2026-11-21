
"""Convert the market price spreadsheet into one CSV file per market.
 
The source timestamps are not used directly: Market 1 has mislabelled rows on
the March clock-change days, and Market 2 timestamps drift by a few
milliseconds. Both sheets have exactly one row per period, so a regular time
grid is rebuilt from the first timestamp and the number of rows.
 
Usage:
    python convert_prices.py path/to/prices.xlsx data/
    
[Claude]: This script has been done using claude. 
"""
 
import sys
from pathlib import Path
 
import pandas as pd
 
# sheet name -> (output file name, time step)
SHEETS = {
    "Half-hourly data": ("market1.csv", "30min"),
    "Hourly data": ("market2.csv", "1h"),
}
 
 
def read_sheet(xlsx_path: Path, sheet: str, freq: str) -> pd.DataFrame:
    """Read one price sheet and return it on a regular time grid."""
    raw = pd.read_excel(xlsx_path, sheet_name=sheet)
    raw.columns = ["timestamp", "price"]
 
    if raw["price"].isna().any():
        raise ValueError(f"{sheet}: {raw['price'].isna().sum()} missing prices")
 
    start = raw["timestamp"].iloc[0].round(freq)
    grid = pd.date_range(start, periods=len(raw), freq=freq)
 
    # Report how many source timestamps disagree with the rebuilt grid
    n_mismatch = (raw["timestamp"].dt.round(freq) != grid).sum()
    if n_mismatch:
        print(f"{sheet}: {n_mismatch} source timestamps differ from the regular grid; "
              "using the regular grid")
 
    return pd.DataFrame({"timestamp": grid, "price_gbp_per_mwh": raw["price"]})
 
 
def convert(xlsx_path: Path, output_dir: Path) -> None:
    """Write one CSV per market and check that the two markets line up."""
    output_dir.mkdir(parents=True, exist_ok=True)
 
    markets = {}
    for sheet, (file_name, freq) in SHEETS.items():
        df = read_sheet(xlsx_path, sheet, freq)
        df.to_csv(output_dir / file_name, index=False)
        markets[sheet] = df
        print(f"{sheet}: {len(df)} rows -> {output_dir / file_name}")
 
    m1 = markets["Half-hourly data"]
    m2 = markets["Hourly data"]
    if len(m1) != 2 * len(m2):
        raise ValueError(f"Market 1 has {len(m1)} rows, expected 2 x {len(m2)} = {2 * len(m2)}")
    if m1["timestamp"].iloc[0] != m2["timestamp"].iloc[0]:
        raise ValueError("the two markets do not start at the same time")
 
 
if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: python convert_prices.py <input.xlsx> <output_dir>")
    convert(Path(sys.argv[1]), Path(sys.argv[2]))
 