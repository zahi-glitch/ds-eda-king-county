"""All the numbers of the talk, in one place.

This file is imported by 02_make_report.py (writes the numbers to reports/numbers.md) and by
03_make_images.py (draws the pictures). It does not draw and it does not write any file.

It reads data/processed/king_county_clean.csv, so run 01_clean_data.py first.
Read it from top to bottom: rules -> tables -> one section per hypothesis.
"""

import math
import os
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)                                      # all paths in the scripts are relative to the project root

# =============================================================================================
# 1. THE RULES (change one here, re-run 02 and 03, then update the slides by hand: see reports/numbers.md)
# =============================================================================================
PERCENTILE = 0.25        # "lower-priced" zipcode = its median price is in the cheapest 25% of zipcode medians
MIN_SALES = 30           # a condition or grade level with fewer sales than this is not drawn
HOLD = 6                 # months between buying and selling (H3)
CENTER = (47.6062, -122.3321)    # downtown Seattle (lat, lon): used to say "north / south of downtown"

# =============================================================================================
# 2. THE TABLES
# =============================================================================================
df = pd.read_csv("data/processed/king_county_clean.csv", parse_dates=["date"], dtype={"zipcode": str})
sold = df.dropna(subset=["price"]).copy()           # one row per sale
sold["ppsf"] = sold["price"] / sold["sqft_living"]  # price per sqft
houses = df.drop_duplicates(subset="id")            # one row per house (a house sold twice counts once)

zips = (sold.groupby("zipcode")["price"].agg(median_price="median", n_sales="count").sort_values("median_price"))
cutoff = zips["median_price"].quantile(PERCENTILE)  # median price of a zipcode must be at most this
low_set = set(zips.index[zips["median_price"] <= cutoff])      # the lower-priced zipcodes
low = sold[sold["zipcode"].isin(low_set)].copy()               # their sales
rest = sold[~sold["zipcode"].isin(low_set)]                    # all other sales

# =============================================================================================
# 3. THE DATA (slides 3 and 4)
# =============================================================================================
n_houses = houses["id"].nunique()
n_sales = len(sold)
n_zips = len(zips)
county_median = sold["price"].median()
date_first, date_last = sold["date"].min(), sold["date"].max()
n_months_data = (date_last.year - date_first.year) * 12 + date_last.month - date_first.month + 1
price_cap = 1_500_000                               # the histogram stops here
n_above_cap = int((sold["price"] > price_cap).sum())
price_max = sold["price"].max()

# =============================================================================================
# 4. H1 WHERE (slides 6 and 7)
# =============================================================================================
n_low = len(low_set)
houses_low = houses[houses["zipcode"].isin(low_set)]
share_houses_low = 100 * houses_low["id"].nunique() / n_houses
low_median = low["price"].median()
gap_low = 100 * (1 - low_median / county_median)    # how far below the county median
rest_median = rest["price"].median()
plain_low = 100 * (low["grade"] <= 6).mean()         # % of sales built to a lower standard (grade 6 or lower)
plain_rest = 100 * (rest["grade"] <= 6).mean()

# one row per zipcode: latitude (median of its houses) and median price
zip_lat = pd.DataFrame({"lat": houses.groupby("zipcode")["lat"].median(), "price": zips["median_price"]}).dropna()
south = zip_lat["lat"] < CENTER[0]                  # south of downtown Seattle
n_south, n_north = int(south.sum()), int((~south).sum())
n_low_south = int((zip_lat.index.isin(low_set) & south).sum())
n_low_north = int((zip_lat.index.isin(low_set) & ~south).sum())

# =============================================================================================
# 5. H2 WHAT: does quality raise the price per sqft?  (slide 8, lower-priced zipcodes only)
# =============================================================================================
low["grade_lab"] = pd.cut(low["grade"], [0, 5, 6, 7, 8, 9, 99], labels=["5-", "6", "7", "8", "9", "10+"])   # grade in 6 groups
quality = low[["condition", "grade", "ppsf", "sqft_living", "grade_lab"]].dropna()

# median price per sqft at each level (the two charts)
cond_table = quality.groupby("condition")["ppsf"].agg(median="median", n="count")
grade_table = quality.groupby("grade_lab", observed=True)["ppsf"].agg(median="median", n="count")

pct = lambda v: 100 * (np.exp(v) - 1)               # a log difference as a percent


def _design(d):
    return np.c_[np.ones(len(d)), d["condition"].to_numpy(), d["grade"].to_numpy()]


# --- The simple numbers on the slide: medians that can be read off the two charts
_cm = cond_table[cond_table["n"] >= MIN_SALES]["median"]
cond5_median = _cm.loc[5]                                   # condition 5 (the best)
cond_2_4_low, cond_2_4_high = _cm.loc[2:4].min(), _cm.loc[2:4].max()     # conditions 2 to 4
cond_2_4_typical = round(_cm.loc[2:4].mean(), -1)            # about $160, rounded to the nearest 10
cond5_vs_3 = 100 * (_cm.loc[5] / _cm.loc[3] - 1)            # condition 5 against the typical house (condition 3), in %
_gm = grade_table.loc[["7", "8", "9", "10+"], "median"]
grade_7up_low, grade_7up_high = _gm.min(), _gm.max()        # median price per sqft, grade 7 to 10+
share_grade_7up = 100 * (quality["grade"] >= 7).mean()      # % of sales that are grade 7 or higher
share_cond5 = 100 * (quality["condition"] == 5).mean()      # % of sales in condition 5

# --- Detail for questions (not on the slides): a regression of the log price per sqft on condition and grade.
# Effect of ONE step of condition (or grade) on the price per sqft, each adjusted for the other.
# log-linear fit; 95% interval from 2,000 bootstrap resamples of the sales.
_y, _X = np.log(quality["ppsf"].to_numpy()), _design(quality)
_fit = lambda idx: np.linalg.lstsq(_X[idx], _y[idx], rcond=None)[0]
_b = _fit(np.arange(len(quality)))
_rng = np.random.default_rng(7)
_bs = np.array([_fit(_rng.integers(0, len(quality), len(quality))) for _ in range(2000)])
cond_effect = pct(_b[1])
cond_ci = pct(np.percentile(_bs[:, 1], [2.5, 97.5]))

# the same for grade, using only grade 7 and above (below that the price per sqft falls, then it is flat)
_q7 = quality[quality["grade"] >= 7]
_y7, _X7 = np.log(_q7["ppsf"].to_numpy()), _design(_q7)
_fit7 = lambda idx: np.linalg.lstsq(_X7[idx], _y7[idx], rcond=None)[0][2]
_rg = np.random.default_rng(11)
grade7_effect = pct(_fit7(np.arange(len(_q7))))
grade7_ci = pct(np.percentile([_fit7(_rg.integers(0, len(_q7), len(_q7))) for _ in range(1500)], [2.5, 97.5]))

# share of the variation in the price per sqft explained by grade and condition together
_res = _y - _X @ np.linalg.lstsq(_X, _y, rcond=None)[0]
r2_quality = 100 * (1 - _res.var() / _y.var())

# =============================================================================================
# 6. H3 WHEN: what would a 6-month hold have returned?  (slides 10 and 11, lower-priced zipcodes only)
# =============================================================================================
low["month"] = low["date"].dt.to_period("M")
_by_month = {m: x["ppsf"].to_numpy() for m, x in low.dropna(subset=["ppsf"]).groupby("month")}
_months = sorted(_by_month)
n_months = len(_months)

# one row per buying month: (buy month, sell month 6 months later, change %, interval low, interval high)
_rb = np.random.default_rng(2)
hold = []
for i in range(n_months - HOLD):
    a, b = _by_month[_months[i]], _by_month[_months[i + HOLD]]
    change = 100 * (np.median(b) / np.median(a) - 1)
    boot = [100 * (np.median(_rb.choice(b, len(b))) / np.median(_rb.choice(a, len(a))) - 1) for _ in range(1000)]
    hold.append((_months[i], _months[i + HOLD], change, *np.percentile(boot, [2.5, 97.5])))
hold_autumn = [h for h in hold if h[0].month in (9, 10, 11)]        # bought Sep, Oct, Nov
hold_midyear = [h for h in hold if h[0].month in (5, 6, 7, 8)]      # bought May to Aug


def _pooled(rows, seed):
    """All buys of the group against all their sales 6 months later: change in the median price per sqft, 95% interval."""
    buy = np.concatenate([_by_month[h[0]] for h in rows])
    sell = np.concatenate([_by_month[h[1]] for h in rows])
    r = np.random.default_rng(seed)
    boot = [100 * (np.median(r.choice(sell, len(sell))) / np.median(r.choice(buy, len(buy))) - 1) for _ in range(2000)]
    return 100 * (np.median(sell) / np.median(buy) - 1), *np.percentile(boot, [2.5, 97.5])


autumn, autumn_lo, autumn_hi = _pooled(hold_autumn, 3)             # bought Sep to Nov
midyear, midyear_lo, midyear_hi = _pooled(hold_midyear, 4)         # bought May to Aug


# =============================================================================================
# 7. H3 WHEN, as worded: are prices higher in spring and summer than in autumn and winter?  (slides 10 and 11)
# =============================================================================================
month_median = low.dropna(subset=["ppsf"]).groupby("month")["ppsf"].median()     # median price per sqft of each month (13 values)
SEASONS = {"Summer": ("2014-06", "2014-08"), "Autumn": ("2014-09", "2014-11"), "Winter": ("2014-12", "2015-02"), "Spring": ("2015-03", "2015-05")}
WARM, COLD = ("Summer", "Spring"), ("Autumn", "Winter")                          # what is compared: spring and summer against autumn and winter


def _values(names):
    out = []
    for name in names:
        first, last = (pd.Period(m) for m in SEASONS[name])
        out.append(low.loc[(low["month"] >= first) & (low["month"] <= last), "ppsf"].dropna().to_numpy())
    return np.concatenate(out)


season_median = {name: np.median(_values([name])) for name in SEASONS}           # pooled median price per sqft of the 3 months
warm_median, cold_median = np.median(_values(WARM)), np.median(_values(COLD))   # pooled medians of the 6 months
warm_vs_cold = 100 * (warm_median / cold_median - 1)
spring_vs_cold = 100 * (season_median["Spring"] / cold_median - 1)
summer_vs_cold = 100 * (season_median["Summer"] / cold_median - 1)


def _versus_cold(names, seed):
    """Change of the group's median against autumn and winter, with a 95% bootstrap interval (2,000 resamples)."""
    group, cold = _values(names), _values(COLD)
    r = np.random.default_rng(seed)
    boot = [100 * (np.median(r.choice(group, len(group))) / np.median(r.choice(cold, len(cold))) - 1) for _ in range(2000)]
    return np.percentile(boot, [2.5, 97.5])


warm_ci, spring_ci, summer_ci = _versus_cold(WARM, 7), _versus_cold(["Spring"], 5), _versus_cold(["Summer"], 6)
same_month_year_later = 100 * (month_median.iloc[-1] / month_median.iloc[0] - 1)   # May 2015 against May 2014: the trend, not the season


# The ONE example on slide 11: bought in November 2014, sold 6 months later (May 2015), at the median price per sqft of those months.
# November is the middle-to-late autumn month whose result (about +6.5%) is closest to the pooled autumn result: not a cherry-picked month.
EXAMPLE_BUY = pd.Period("2014-11")
example_buy_price = month_median[EXAMPLE_BUY]
example_sell_price = month_median[EXAMPLE_BUY + HOLD]
example_change = 100 * (example_sell_price / example_buy_price - 1)


# Slide 9: which columns go with the price per sqft?  Spearman rank correlation in the lower-priced zipcodes
# (pairwise: "renovated" is only known for 82% of the sales).  A lead for next steps, not a result: price per sqft = price / living area.
CORR_COLUMNS = ["sqft_living", "bedrooms", "bathrooms", "yr_built", "grade", "floors", "view", "condition", "renovated"]
_corr = low[["ppsf"] + CORR_COLUMNS].apply(pd.to_numeric, errors="coerce").corr(method="spearman")
corr_ppsf = _corr.loc["ppsf", CORR_COLUMNS]


# Slide 9: median price per sqft by size of the house (living area), lower-priced zipcodes. Five bands, each with at least 700 sales.
SIZE_EDGES = [0, 1200, 1600, 2000, 2500, 100000]
SIZE_LABELS = ["under 1,200", "1,200-1,600", "1,600-2,000", "2,000-2,500", "over 2,500"]
_sized = low.dropna(subset=["ppsf"])
size_table = _sized.groupby(pd.cut(_sized["sqft_living"], SIZE_EDGES, labels=SIZE_LABELS), observed=True).agg(
    n=("ppsf", "size"), ppsf=("ppsf", "median"), price=("price", "median"))
size_small_ppsf, size_big_ppsf = size_table["ppsf"].iloc[0], size_table["ppsf"].iloc[-1]
size_drop = 100 * (size_big_ppsf / size_small_ppsf - 1)    # smallest to biggest houses: the fall of the median price per sqft (negative)
