# Cleaning log

Written by `src/01_clean_data.py`. Raw file: `data/raw/king_county_joined.csv`.

- Raw file: 21,597 rows, 21 columns. One row is one sale.
- Column names stripped and lower-cased; `date` parsed; `zipcode` kept as a 5-character text label.
- Exact duplicate rows: 0 (none to drop).
- 176 houses appear twice with different sale dates: they were sold twice in the period. They are kept as two sales; analyses that count houses use `id` once.
- `yr_renovated`: 744 values were the year times ten (19910 = 1991); divided by 10. 0 means never renovated.
- `yr_renovated` is missing in 3,848 rows (18%). They are NOT counted as 'not renovated': the new column `renovated` is 1 (renovated), 0 (never) or empty (unknown), and shares are computed among known rows only.
- `sqft_basement`: 452 missing values. In every row where it is known, above + basement = living area, so the missing ones were computed as living - above (an exact recovery, not a guess).
- `bedrooms` = 33 in a 1620 sqft house with 1.75 bathrooms (id 2402100895): almost surely a typo for 3. Set to 3.
- 4 more houses list 10 or more bedrooms (11, 10, 10, 10); odd but possible, left as they are.
- `waterfront`: 2,391 missing values, left empty (unknown). The analysis does not use this column.
- `view`: 63 missing values, left empty (unknown). The analysis does not use this column.
- Checks passed: price present and positive, condition 1-5, grade 1-13, coordinates inside King County, 5-digit zipcodes.
- Prices run from $78,000 to $7,700,000; the very expensive sales are kept (the analysis uses medians). Sale dates: 02 May 2014 to 27 May 2015.
- Clean file: 21,597 rows, 22 columns -> `data/processed/king_county_clean.csv`.
