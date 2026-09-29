import pandas as pd
import pytest
from src.clean import clean
from src.verify import verify, flag_outliers


def sample_df():
    """7 rows where I know exactly what should survive cleaning."""
    return pd.DataFrame({
        "transaction_id": ["T1", "T1", "T2", "T3", "T4", "T5", "T6"],
        "trans_group":    ["Sales", "Sales", "Sales", "Sales", "Sales", "Mortgages", "Sales"],
        "date":           ["01-01-2024", "01-01-2024", "02-01-2024", "not a date",
                           "03-01-2024", "04-01-2024", "05-01-2024"],
        "property_type":  ["Unit", "Unit", "Unit", "Unit", "Unit", "Unit", "Villa"],
        "area":           [" marina", "Marina", "Marina", "Marina", "Downtown",
                           "Marina", "Marina"],
        "price":          [1_000_000, 1_000_000, -5, 900_000, 2_000_000,
                           500_000, 3_000_000],
        "size_sqm":       [100, 100, 80, 90, 150, 60, 200],
    })


def test_clean_keeps_only_valid_apartment_sales():
    clean_df, log = clean(sample_df())
    # 7 in: 1 mortgage, 1 villa, 1 bad date, 1 duplicate id, 1 negative price
    assert len(clean_df) == 2


def test_price_per_sqft_is_correct():
    clean_df, _ = clean(sample_df())
    row = clean_df[clean_df["area"] == "Marina"].iloc[0]
    assert row["price_per_sqft"] == pytest.approx(1_000_000 / (100 * 10.7639))


def test_dates_are_read_day_first():
    clean_df, _ = clean(sample_df())
    assert pd.Timestamp("2024-01-03") in set(clean_df["date"])  # 03-01-2024 = 3 Jan


def test_verify_passes_on_good_data():
    raw = sample_df()
    clean_df, log = clean(raw)
    assert verify(len(raw), clean_df, log) == []


def test_verify_catches_tampering():
    raw = sample_df()
    clean_df, log = clean(raw)
    broken = clean_df.iloc[:-1]  # secretly lose a row
    assert len(verify(len(raw), broken, log)) > 0


def test_outlier_flagger_catches_absurd_price():
    df = pd.DataFrame({
        "area": ["A"] * 6,
        "price_per_sqft": [1000, 1000, 1000, 1000, 1000, 900_000],
    })
    assert len(flag_outliers(df)) == 1