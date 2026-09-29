import pandas as pd

SQM_TO_SQFT = 10.7639


def clean(df):
    """Returns (clean_df, drop_log). drop_log records every removal and why."""
    df = df.copy()
    log = []

    def drop(mask, reason):
        """Remove rows where mask is True, and record how many and why."""
        nonlocal df
        n = int(mask.sum())
        if n:
            log.append({"reason": reason, "rows_dropped": n})
        df = df[~mask]

    # 1. Fix types. errors="coerce" turns bad values into NaN/NaT instead of crashing
    df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y", errors="coerce")
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df["size_sqm"] = pd.to_numeric(df["size_sqm"], errors="coerce")

    # 2. Standardize text so "Marina" and " marina" count as one area
    df["area"] = df["area"].astype("string").str.strip().str.title()

    # 3. Keep only what a price-per-sqft calculation makes sense for
    drop(df["trans_group"] != "Sales", "not a sale (mortgage, gift, etc.)")
    drop(df["property_type"] != "Unit", "not an apartment unit (villa, land, building)")

    # 4. Quality rules
    drop(df[["date", "area", "price", "size_sqm"]].isna().any(axis=1),
         "missing or unparseable value")
    drop(df.duplicated(subset="transaction_id"), "duplicate transaction_id")
    drop(df["price"] <= 0, "price <= 0")
    drop(df["size_sqm"] <= 0, "size <= 0")

    # 5. Derived columns
    df["size_sqft"] = df["size_sqm"] * SQM_TO_SQFT
    df["price_per_sqft"] = df["price"] / df["size_sqft"]

    drop_log = pd.DataFrame(log, columns=["reason", "rows_dropped"])
    return df.reset_index(drop=True), drop_log