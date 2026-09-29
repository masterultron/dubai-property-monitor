import pandas as pd
from src.config import DATA_PATH, COLUMN_MAP


def load_raw(path=DATA_PATH, nrows=None):
    # Check the header first (reads 0 rows, so it's instant)
    header = pd.read_csv(path, nrows=0).columns
    missing = [c for c in COLUMN_MAP if c not in header]
    if missing:
        raise ValueError(f"CSV is missing expected columns: {missing}")

    # usecols: read only the 7 columns we need, not all 46
    df = pd.read_csv(path, usecols=list(COLUMN_MAP), nrows=nrows)
    return df.rename(columns=COLUMN_MAP)