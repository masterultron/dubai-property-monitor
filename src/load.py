import os
import pandas as pd
from src.config import DATA_PATH, SAMPLE_PATH, COLUMN_MAP


def load_raw(path=None, nrows=None):
    # Use the full DLD file if present, otherwise the small committed sample
    if path is None:
        path = DATA_PATH if os.path.exists(DATA_PATH) else SAMPLE_PATH
    print(f"Loading data from: {path}")

    # Check the header first (reads 0 rows, so it's instant)
    header = pd.read_csv(path, nrows=0).columns
    missing = [c for c in COLUMN_MAP if c not in header]
    if missing:
        raise ValueError(f"CSV is missing expected columns: {missing}")

    df = pd.read_csv(path, usecols=list(COLUMN_MAP), nrows=nrows)
    return df.rename(columns=COLUMN_MAP)