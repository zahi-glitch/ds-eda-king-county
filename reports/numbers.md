# Numbers of the talk

Written by `src/02_make_report.py`. Every number on a slide is listed here. The slides are plain TeX with these numbers typed in:
if a number changes, edit the slide (the column *slide file* tells which one). The last section lists the numbers that are only in pictures.

| slide file | what | as written on the slide | exact value |
|---|---|---|---|
| `04_data_details.tex` | houses (a house sold twice counts once) | 21,420 | 21420 |
| `04_data_details.tex` | sales | 21,597 | 21597 |
| `04_data_details.tex` | zipcodes | 70 |  |
| `04_data_details.tex` | median sale price, whole county | $450,000 | 450000.0 |
| `04_data_details.tex` | first month of sales | May 2014 |  |
| `04_data_details.tex` | last month of sales | May 2015 |  |
| `04_data_details.tex` | number of months | 13 months |  |
| `06_h1_where.tex` | lower-priced zipcodes | 18 of 70 |  |
| `07_focus.tex` | number of lower-priced zipcodes | 18 zipcodes |  |
| `08_h2_quality.tex` | median price per sqft, condition 5 | $186 |  |
| `10_h3_when.tex` | spring and summer together, median price per sqft above autumn and winter together | 3% |  |
| `10_h3_when.tex` | spring (Mar to May 2015) alone above autumn and winter (Sep to Feb) | 7% |  |
| `11_h3_example.tex` | example: median price per sqft, November 2014 (bought) | $162 |  |
| `11_h3_example.tex` | example: median price per sqft, May 2015 (sold 6 months later) | $173 |  |
| `11_h3_example.tex` | example: change from November to May | +6.6% |  |
| `12_insights.tex` | the lower-priced zipcodes are this far below the county median | 38% |  |
| `12_insights.tex` | condition 5 against condition 3, price per sqft | 18% |  |
| `12_insights.tex` | spring above autumn and winter | 7% |  |
| `13_advice.tex` | bought Sep to Nov, sold 6 months later | +6% | 6.46 |
| `09_h2_more.tex` | median price per sqft, biggest vs smallest houses (over 2,500 vs under 1,200 sqft) | 34% |  |
| `09_h2_more.tex` | median price per sqft, smallest houses (under 1,200 sqft) | $208 |  |
| `09_h2_more.tex` | median price per sqft, biggest houses (over 2,500 sqft) | $138 |  |
| `14_wrap_up.tex` | months of past sales | 13 months |  |

## Numbers that are only in pictures

| picture | numbers |
|---|---|
| `slide 9 sentence (sizes)` | median price per sqft by living area: under 1,200 sqft $208 (n=941, median price $209,500), 1,200-1,600 sqft $175 (n=1151, median price $245,000), 1,600-2,000 sqft $153 (n=1170, median price $275,000), 2,000-2,500 sqft $145 (n=995, median price $325,000), over 2,500 sqft $138 (n=762, median price $402,448) |
| `pres_corr.png (slide 9)` | rank correlation of price per sqft with the other columns: sqft_living -0.51, bedrooms -0.38, bathrooms -0.32, yr_built -0.22, grade -0.21, floors -0.19, renovated +0.07, condition +0.10, view +0.16 |
| `pres_south.png (slide 6)` | median price of each zipcode against latitude; the 25th percentile limit is $320,000 (18 zipcodes at or below it) |
| `(not on a slide)` | limit $320,000; 23% of all houses; median price 38% below the county |
| `pres_prices.png (slide 4)` | histogram of sale prices, bars every $50,000, up to $1,500,000 |
| `pres_focus_prices.png (slide 7)` | sale prices, boxes (middle half of the sales, whiskers 5% to 95%): median of lower-priced $277,000 vs others $524,975 |
| `pres_focus_grade.png (slide 7)` | sales built to a lower standard (grade 6 or lower): lower-priced 18% vs others 9% |
| `pres_quality_condition.png (slide 8)` | median price per sqft by condition: 1: $176 (n=7), 2: $159 (n=58), 3: $158 (n=3179), 4: $164 (n=1478), 5: $186 (n=297) |
| `pres_quality_grade.png (slide 8)` | median price per sqft by grade: 5-: $190 (n=113), 6: $190 (n=777), 7: $161 (n=2555), 8: $150 (n=1160), 9: $156 (n=324), 10+: $159 (n=90) |
| `pres_when.png (slide 10), pres_when_example.png (slide 11)` | median price per sqft by month: May 2014 $155, Jun 2014 $157, Jul 2014 $158, Aug 2014 $161, Sep 2014 $159, Oct 2014 $158, Nov 2014 $162, Dec 2014 $157, Jan 2015 $160, Feb 2015 $159, Mar 2015 $167, Apr 2015 $172, May 2015 $173 |
| `pres_when.png (slide 10), pres_when_example.png (slide 11)` | median of the 3 months: Summer $159, Autumn $159, Winter $159, Spring $170 |

## Detail for questions (not on the slides)

- Regression of the log price per sqft on condition and grade (lower-priced zipcodes, 5,019 sales), each adjusted for the other.
- One step of condition: +3% per step (95% interval +2% to +5%, 2,000 bootstrap resamples). It is an average: the medians are flat from condition 2 to 4 and jump at 5.
- One step of grade, grade 7 and up: -1% per step (95% interval -2% to 0%): no clear effect.
- Grade and condition together explain 4% of the variation in the price per sqft.
- H3 as worded: spring and summer together (Jun to Aug 2014, Mar to May 2015) vs autumn and winter together (Sep 2014 to Feb 2015): +2.7% (95% interval +1.2 to +4.5); spring alone: +6.7% (+4.3 to +9.1); summer alone: +0.0% (-2.3 to +1.8). Pooled medians of the months, 2,000 bootstrap resamples.
- Trend check: May 2015 against May 2014, the same month a year apart: +11.2%. So the spring rise can also be a general price rise.
- 6-month hold (buy in a month, sell 6 months later), used for the +6% on slides 10 to 11: H3 as a decision rule, bought Sep to Nov and sold 6 months later: +6% (95% interval +4% to +9%). Bought May to Aug: +1% (95% interval -1% to +3%), no clear gain.
- The thin black line on each bar of the H3 chart is its own 95% interval. November's starts below zero, so a single month is uncertain; pooling Sep to Nov gives the interval above.
- Below grade 7 the price per sqft is higher (about $190), but those are small houses, and smaller houses cost more per sqft.

## How to read the method

- **Lower-priced zipcode**: the median sale price of the zipcode is among the cheapest 25% of the 70 zipcodes (at most $320,000).
- **H2**: median price per sqft at each condition and each grade, lower-priced zipcodes only; levels with fewer than 30 sales are left out.
- **H3**: median price per sqft of the lower-priced zipcodes in the month bought against 6 months later; the 95% interval comes from bootstrap resamples. With only 13 months of data, season and general trend cannot be told apart.
