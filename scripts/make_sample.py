import pandas as pd
from src.config import DATA_PATH, COLUMN_MAP

SAMPLE_PATH = "data/sample_transactions.csv"

# Read only the 7 columns we use, then take a reproducible random sample
df = pd.read_csv(DATA_PATH, usecols=list(COLUMN_MAP))
sample = df.sample(n=100_000, random_state=42)  # random_state = same sample every time
sample.to_csv(SAMPLE_PATH, index=False)
print(f"Wrote {len(sample):,} rows to {SAMPLE_PATH}")