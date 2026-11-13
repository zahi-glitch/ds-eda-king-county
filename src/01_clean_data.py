"""Step 1: clean the raw King County sales file.

Reads   data/raw/king_county_joined.csv
Writes  data/processed/king_county_clean.csv     the file every other script uses
        reports/cleaning_log.md                  what was checked and what was changed

Run from the project root:
    python src/01_clean_data.py

Rule of this script: fix what is clearly a recording error, flag what is only suspicious,
and never fill a gap with a guess. Every change is counted in the log.
"""

from pathlib import Path

import numpy as np
import pandas as pd

RAW = Path("data/raw/king_county_joined.csv")
CLEAN = Path("data/processed/king_county_clean.csv")
LOG = Path("reports/cleaning_log.md")

log = []                                   # lines of the cleaning log


def note(text):
    log.append(text)
    print(text)


# ------------------------------------------------------------ 1. Read and look
df = pd.read_csv(RAW)
n_raw = len(df)
note(f"- Raw file: {n_raw:,} rows, {df.shape[1]} columns. One row is one sale.")

# ------------------------------------------------------------ 2. Names and types
df.columns = df.columns.str.strip().str.lower()
df["date"] = pd.to_datetime(df["date"])
df["zipcode"] = df["zipcode"].astype(int).astype(str).str.zfill(5)      # a label, not a number
for col in ("bedrooms", "bathrooms", "floors"):
    df[col] = df[col].astype(float)
note("- Column names stripped and lower-cased; `date` parsed; `zipcode` kept as a 5-character text label.")

# ------------------------------------------------------------ 3. Duplicates
n_full_dup = int(df.duplicated().sum())
df = df.drop_duplicates()
n_resold = int((df.groupby("id").size() > 1).sum())
note(f"- Exact duplicate rows: {n_full_dup} (none to drop).")
note(f"- {n_resold} houses appear twice with different sale dates: they were sold twice in the period. "
     "They are kept as two sales; analyses that count houses use `id` once.")

# ------------------------------------------------------------ 4. Renovation year recorded ten times too large
big = df["yr_renovated"] > 2100                                       # e.g. 19910 means 1991
n_fix_ren = int(big.sum())
df.loc[big, "yr_renovated"] = df.loc[big, "yr_renovated"] / 10
bad_year = df["yr_renovated"].dropna().loc[lambda s: (s > 0) & ((s < 1900) | (s > 2015))]
assert bad_year.empty, "renovation years outside 1900-2015 remain"
note(f"- `yr_renovated`: {n_fix_ren} values were the year times ten (19910 = 1991); divided by 10. 0 means never renovated.")
n_ren_missing = int(df["yr_renovated"].isna().sum())
df["renovated"] = np.where(df["yr_renovated"].isna(), np.nan, (df["yr_renovated"] > 0).astype(float))
note(f"- `yr_renovated` is missing in {n_ren_missing:,} rows ({100 * n_ren_missing / len(df):.0f}%). They are NOT counted as 'not renovated': "
     "the new column `renovated` is 1 (renovated), 0 (never) or empty (unknown), and shares are computed among known rows only.")

# ------------------------------------------------------------ 5. Basement area can be recovered exactly
known = df["sqft_basement"].notna()
assert (abs(df.loc[known, "sqft_above"] + df.loc[known, "sqft_basement"] - df.loc[known, "sqft_living"]) <= 1).all()
n_base = int((~known).sum())
df.loc[~known, "sqft_basement"] = df.loc[~known, "sqft_living"] - df.loc[~known, "sqft_above"]
note(f"- `sqft_basement`: {n_base} missing values. In every row where it is known, above + basement = living area, "
     "so the missing ones were computed as living - above (an exact recovery, not a guess).")

# ------------------------------------------------------------ 6. An impossible number of bedrooms
typo = (df["bedrooms"] >= 30)
n_typo = int(typo.sum())
for _, r in df[typo].iterrows():
    note(f"- `bedrooms` = {r['bedrooms']:.0f} in a {r['sqft_living']:.0f} sqft house with {r['bathrooms']} bathrooms (id {int(r['id'])}): "
         "almost surely a typo for 3. Set to 3.")
df.loc[typo, "bedrooms"] = 3.0
many = df[(df["bedrooms"] >= 10)]
note(f"- {len(many)} more houses list 10 or more bedrooms ({', '.join(str(int(b)) for b in many['bedrooms'])}); odd but possible, left as they are.")

# ------------------------------------------------------------ 7. Gaps that are not needed and are left empty
for col in ("waterfront", "view"):
    n_na = int(df[col].isna().sum())
    note(f"- `{col}`: {n_na:,} missing values, left empty (unknown). The analysis does not use this column.")

# ------------------------------------------------------------ 8. Sanity checks (the script stops if one fails)
assert df["price"].notna().all() and (df["price"] > 0).all(), "price must be present and positive"
assert df["sqft_living"].gt(0).all()
assert df["condition"].between(1, 5).all() and df["grade"].between(1, 13).all()
assert df["lat"].between(47, 48).all() and df["long"].between(-123, -121).all()
assert df["zipcode"].str.len().eq(5).all()
note(f"- Checks passed: price present and positive, condition 1-5, grade 1-13, coordinates inside King County, 5-digit zipcodes.")
note(f"- Prices run from ${df['price'].min():,.0f} to ${df['price'].max():,.0f}; the very expensive sales are kept (the analysis uses medians). "
     f"Sale dates: {df['date'].min():%d %b %Y} to {df['date'].max():%d %b %Y}.")

# ------------------------------------------------------------ 9. Write
df = df.reset_index(drop=True)                      # keep the order of the raw file
CLEAN.parent.mkdir(parents=True, exist_ok=True)
LOG.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(CLEAN, index=False)
note(f"- Clean file: {len(df):,} rows, {df.shape[1]} columns -> `{CLEAN}`.")

LOG.write_text("# Cleaning log\n\nWritten by `src/01_clean_data.py`. Raw file: `data/raw/king_county_joined.csv`.\n\n" + "\n".join(log) + "\n", encoding="utf-8")
print(f"[saved] {CLEAN} and {LOG}")
