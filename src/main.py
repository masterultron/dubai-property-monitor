import os
import sys
import pandas as pd
from src.load import load_raw
from src.clean import clean
from src.verify import verify, flag_outliers
from src.analyze import price_per_sqft_by_area, monthly_counts


def build_summary(raw_rows, clean_df, problems, outliers):
    # Rank areas on the latest 12 months IN THE DATA, not all 20 years
    latest = clean_df["date"].max()
    recent = clean_df[clean_df["date"] > latest - pd.DateOffset(months=12)]
    top = price_per_sqft_by_area(recent).head(5)
    monthly = monthly_counts(clean_df).tail(3)
    partial = latest != latest + pd.offsets.MonthEnd(0)  # True if data stops mid-month

    lines = ["Dubai Property Monitor", ""]
    lines.append(f"Rows in: {raw_rows:,} | Apartment sales used: {len(clean_df):,}")
    lines.append(f"Data runs to: {latest.date()}")
    lines.append("")
    lines.append("Top 5 areas by median AED/sqft (last 12 months of data):")
    for area, r in top.iterrows():
        lines.append(f"  {area}: {r['median_ppsf']:,.0f} ({int(r['deals'])} deals)")
    lines.append("")
    lines.append("Apartment sales, latest 3 months:")
    for i, (period, n) in enumerate(monthly.items()):
        note = " (partial month)" if partial and i == len(monthly) - 1 else ""
        lines.append(f"  {period}: {n:,}{note}")
    lines.append("")
    lines.append(f"Flagged outliers for review: {len(outliers)}")
    if problems:
        lines.append("")
        lines.append("VERIFICATION FAILED:")
        lines.extend(f"  - {p}" for p in problems)
    else:
        lines.append("All verification checks passed.")
    return "\n".join(lines)


def run(notify=False, nrows=None):
    raw = load_raw(nrows=nrows)
    clean_df, drop_log = clean(raw)
    problems = verify(len(raw), clean_df, drop_log)
    outliers = flag_outliers(clean_df)

    summary = build_summary(len(raw), clean_df, problems, outliers)
    print(summary)
    print("\nDrop log:\n", drop_log.to_string(index=False))

    os.makedirs("output", exist_ok=True)
    outliers.to_csv("output/flagged_outliers.csv", index=False)

    if notify:
        from src.notify import send_telegram  # imported only when needed
        send_telegram(summary)


if __name__ == "__main__":
    run(notify="--notify" in sys.argv)