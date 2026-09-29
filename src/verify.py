import pandas as pd


def verify(raw_rows, clean_df, drop_log):
    """Returns a list of problems. Empty list = all checks passed."""
    problems = []

    # Check 1: the numbers must add up. raw - dropped = clean
    dropped = int(drop_log["rows_dropped"].sum()) if not drop_log.empty else 0
    if raw_rows - dropped != len(clean_df):
        problems.append(
            f"Row count mismatch: {raw_rows} raw - {dropped} dropped != {len(clean_df)} clean"
        )

    # Check 2: no impossible values survived cleaning
    if (clean_df["price"] <= 0).any():
        problems.append("Non-positive prices found after cleaning")
    if (clean_df["size_sqft"] <= 0).any():
        problems.append("Non-positive sizes found after cleaning")

    # Check 3: no dates in the future
    if (clean_df["date"] > pd.Timestamp.today()).any():
        problems.append("Transactions dated in the future")

    # Check 4: nothing empty in key columns
    if clean_df[["date", "area", "price", "price_per_sqft"]].isna().any().any():
        problems.append("Missing values remain in key columns")

    # Check 5: nothing left over that should have been filtered out
    if not (clean_df["trans_group"] == "Sales").all():
        problems.append("Non-sale rows remain after cleaning")

    if len(clean_df) == 0:
        problems.append("Clean dataset is empty")

    return problems


def flag_outliers(df, low=0.2, high=5.0):
    """Flag rows whose price/sqft is far from their area's median."""
    area_median = df.groupby("area")["price_per_sqft"].transform("median")
    ratio = df["price_per_sqft"] / area_median
    return df[(ratio < low) | (ratio > high)]