def price_per_sqft_by_area(df, min_deals=20):
    result = (
        df.groupby("area")
        .agg(
            deals=("price", "size"),
            median_ppsf=("price_per_sqft", "median"),
            avg_price=("price", "mean"),
        )
        .query("deals >= @min_deals")
        .sort_values("median_ppsf", ascending=False)
    )
    return result.round(0)


def monthly_counts(df):
    return df.groupby(df["date"].dt.to_period("M")).size()