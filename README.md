# King County housing: where should Erin buy?

A 10-minute presentation for **Erin Robinson**, who wants to buy, improve and resell houses in King County, Washington, fairly and with a small profit.
The data are 21,597 house sales from May 2014 to May 2015, plus a map of the zipcodes (both in `data/raw/`).

The finished talk is in `output/`:
- `King_County_talk.pdf`: the talk with pauses (one click reveals the next part of a slide).
- `King_County_talk_no_pauses.pdf`: the same slides, everything shown at once.

## The three questions and the answers

| | Question | Answer |
|---|---|---|
| **H1 Where?** | Where are the lower-priced zipcodes? | 18 of 70 zipcodes (median price at most $320,000, the cheapest quarter). All are in the south: 18 of 40 southern zipcodes, none of 30 northern ones. |
| **H2 What?** | Does quality raise the price per sqft? | Only the best condition pays: condition 5 sells for $186 per sqft, conditions 2 to 4 for $158 to $164. A higher grade adds nothing from grade 7 up. 82% of sales are already grade 7 or higher; only 6% are condition 5. |
| **H3 When?** | Are prices higher in spring and summer than in autumn and winter? | Spring and summer together are about 3% above autumn and winter, but all of it is spring (about 7%, Mar to May 2015); summer is level. Buying in Sep to Nov and selling 6 months later gained about 6%. With one year of data, season and general trend cannot be told apart (May 2015 is also 11% above May 2014). |

## How it works

```
data/raw  ->  01_clean_data.py  ->  data/processed/king_county_clean.csv
                                           |
               02_make_report.py   ->  reports/numbers.md      every number of the talk, in a table
               03_make_images.py   ->  images/*.png            every picture of the talk
                                           |
               slides/*.tex        (plain TeX that you edit by hand, numbers typed in as text)
                                           |  latexmk
                                       output/King_County_talk.pdf
```

- Python makes the numbers and the pictures. It never writes the slides, so nothing you edit by hand is overwritten.
- `02_make_report.py` also checks the slides: for each number in `reports/numbers.md` it looks for the same number on the slide and tells you which slide to fix if it is missing.
- All numbers come from `src/analysis.py`. Read it from top to bottom: rules, tables, then one section per hypothesis.

## Run it

You need [uv](https://docs.astral.sh/uv/getting-started/installation/) and, for the PDF, LaTeX with `latexmk` (TeX Live, MacTeX or MiKTeX).

```bash
cd ds-eda-king-county
uv sync                                  # installs Python and the packages
uv run python src/run_all.py             # all steps in order, including both PDFs
```

Or one step at a time:

```bash
uv run python src/01_clean_data.py       # raw -> clean data, writes reports/cleaning_log.md
uv run python src/02_make_report.py      # numbers -> reports/numbers.md, checks the slides, writes speaker notes
uv run python src/03_make_images.py      # pictures -> images/
cd slides && latexmk -pdf main.tex       # slides -> slides/main.pdf (main_nopauses.tex for the version without pauses)
```

## Folder map

```
ds-eda-king-county/
├── data/
│   ├── raw/                 original files, never edited
│   └── processed/           king_county_clean.csv (made by step 1)
├── src/
│   ├── 01_clean_data.py     raw data -> clean data
│   ├── analysis.py          all the numbers (imported by steps 2 and 3)
│   ├── 02_make_report.py    numbers -> reports/numbers.md, speaker notes, slide check
│   ├── 03_make_images.py    numbers -> pictures
│   └── run_all.py           runs everything in order
├── slides/
│   ├── preamble.tex         colours, fonts, footer and the building blocks (\knote, \knum, \card, \atpos, \atfrom)
│   ├── main.tex             the talk: lists the slide files in order
│   ├── main_nopauses.tex    the same talk with all pauses switched off
│   └── 01_title.tex ... 14_wrap_up.tex     one file per slide
├── images/                  pictures made by step 3
├── assets/                  title picture and the original historical map (credit below)
├── output/                  the two finished PDFs
└── reports/                 numbers.md, speaker_notes.txt, talk_script.md, cleaning_log.md
```

## Data cleaning in short

Details with numbers: `reports/cleaning_log.md`.

- `yr_renovated` was stored multiplied by 10 for 744 rows (19910 = 1991): fixed. Its 3,848 missing values mean *unknown*, not "never renovated".
- `sqft_basement` was missing in 452 rows: recovered exactly as living area minus above-ground area.
- One house with 33 bedrooms (1,620 sqft) is almost surely 3: fixed.
- 176 houses were sold twice in the year: kept as two sales.
- No exact duplicates. Very expensive sales are kept because the analysis uses medians.

## Assumptions and limits

- Lower-priced: the median sale price of the zipcode is in the cheapest quarter of zipcodes.
- Small profit: about 5-10% above total costs. Responsible: modest markups, no quick flips.
- Only 13 months of sales: season and general trend overlap, so H3 is a hint, not proof.
- Renovation costs are not in the data. A low price can hide defects.

## Credits

- Historical map of King County (A. Anderson, 1894), Washington State University Libraries, used as the title picture: `assets/source/`.
