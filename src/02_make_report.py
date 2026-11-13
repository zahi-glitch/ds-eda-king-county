"""Step 2: write the numbers of the talk to reports/numbers.md, and check that the slides show the same numbers.

    python src/02_make_report.py

The slides (slides/*.tex) are plain TeX with the numbers typed in, so a human can read and edit them.
This script is the safety net: for every number in the table below it checks that the slide really shows it.
If you change a rule in analysis.py, run this and it tells you which slides to update by hand.
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analysis import *          # noqa: E402,F403   (the numbers)

money = lambda x: f"${x:,.0f}"                              # 450000 -> $450,000
sp = lambda v: re.sub(r"^[+-]0%$", "0%", f"{v:+.0f}%")      # +3%  -1%  0%   (never +0% or -0%)

# ---------------------------------------------------------------------------------------------
# One line per number that is written on a slide:  (slide file, what it is, exactly as written on the slide)
# ---------------------------------------------------------------------------------------------
ON_SLIDES = [
    ("04_data_details", "houses (a house sold twice counts once)", f"{n_houses:,}"),
    ("04_data_details", "sales", f"{n_sales:,}"),
    ("04_data_details", "zipcodes", f"{n_zips}"),
    ("04_data_details", "median sale price, whole county", money(county_median)),
    ("04_data_details", "first month of sales", f"{date_first:%B %Y}"),
    ("04_data_details", "last month of sales", f"{date_last:%B %Y}"),
    ("04_data_details", "number of months", f"{n_months_data} months"),
    ("06_h1_where", "lower-priced zipcodes", f"{n_low} of {n_zips}"),
    ("07_focus", "number of lower-priced zipcodes", f"{n_low} zipcodes"),
    ("08_h2_quality", "median price per sqft, condition 5", money(cond5_median)),
    ("10_h3_when", "spring and summer together, median price per sqft above autumn and winter together", f"{warm_vs_cold:.0f}%"),
    ("10_h3_when", "spring (Mar to May 2015) alone above autumn and winter (Sep to Feb)", f"{spring_vs_cold:.0f}%"),
    ("11_h3_example", "example: median price per sqft, November 2014 (bought)", money(example_buy_price)),
    ("11_h3_example", "example: median price per sqft, May 2015 (sold 6 months later)", money(example_sell_price)),
    ("11_h3_example", "example: change from November to May", f"{example_change:+.1f}%"),
    ("12_insights", "the lower-priced zipcodes are this far below the county median", f"{gap_low:.0f}%"),
    ("12_insights", "condition 5 against condition 3, price per sqft", f"{cond5_vs_3:.0f}%"),
    ("12_insights", "spring above autumn and winter", f"{spring_vs_cold:.0f}%"),
    ("13_advice", "bought Sep to Nov, sold 6 months later", sp(autumn)),
    ("09_h2_more", "median price per sqft, biggest vs smallest houses (over 2,500 vs under 1,200 sqft)", f"{abs(size_drop):.0f}%"),
    ("09_h2_more", "median price per sqft, smallest houses (under 1,200 sqft)", money(size_small_ppsf)),
    ("09_h2_more", "median price per sqft, biggest houses (over 2,500 sqft)", money(size_big_ppsf)),
    ("14_wrap_up", "months of past sales", f"{n_months_data} months"),
]

# numbers that appear only inside the pictures (nothing to check in the TeX)
IN_PICTURES = [
    ("slide 9 sentence (sizes)", "median price per sqft by living area: " + ", ".join(f"{k} sqft ${r['ppsf']:.0f} (n={int(r['n'])}, median price {money(r['price'])})" for k, r in size_table.iterrows())),
    ("pres_corr.png (slide 9)", "rank correlation of price per sqft with the other columns: " + ", ".join(f"{c} {v:+.2f}" for c, v in corr_ppsf.sort_values().items())),
    ("pres_south.png (slide 6)", f"median price of each zipcode against latitude; the 25th percentile limit is {money(cutoff)} ({n_low} zipcodes at or below it)"),
    ("(not on a slide)", f"limit {money(cutoff)}; {share_houses_low:.0f}% of all houses; median price {gap_low:.0f}% below the county"),
    ("pres_prices.png (slide 4)", "histogram of sale prices, bars every $50,000, up to " + money(price_cap)),
    ("pres_focus_prices.png (slide 7)", f"sale prices, boxes (middle half of the sales, whiskers 5% to 95%): median of lower-priced {money(low_median)} vs others {money(rest_median)}"),
    ("pres_focus_grade.png (slide 7)", f"sales built to a lower standard (grade 6 or lower): lower-priced {plain_low:.0f}% vs others {plain_rest:.0f}%"),
    ("pres_quality_condition.png (slide 8)", "median price per sqft by condition: " + ", ".join(f"{c}: ${r['median']:.0f} (n={int(r['n'])})" for c, r in cond_table.iterrows())),
    ("pres_quality_grade.png (slide 8)", "median price per sqft by grade: " + ", ".join(f"{g}: ${r['median']:.0f} (n={int(r['n'])})" for g, r in grade_table.iterrows())),
    ("pres_when.png (slide 10), pres_when_example.png (slide 11)", "median price per sqft by month: " + ", ".join(f"{m.strftime('%b %Y')} ${v:.0f}" for m, v in month_median.items())),
    ("pres_when.png (slide 10), pres_when_example.png (slide 11)", "median of the 3 months: " + ", ".join(f"{k} ${v:.0f}" for k, v in season_median.items())),
]

# ---------------------------------------------------------------------------------------------
# 1. reports/numbers.md : the table a human reads
# ---------------------------------------------------------------------------------------------
lines = ["# Numbers of the talk", "",
         "Written by `src/02_make_report.py`. Every number on a slide is listed here. The slides are plain TeX with these numbers typed in:",
         "if a number changes, edit the slide (the column *slide file* tells which one). The last section lists the numbers that are only in pictures.", "",
         "| slide file | what | as written on the slide | exact value |", "|---|---|---|---|"]
exact = {"houses (a house sold twice counts once)": n_houses, "sales": n_sales, "median sale price, whole county": county_median,
         "share of all houses in them": round(share_houses_low, 2), "their median price is this far below the county": round(gap_low, 2),
         "effect of one condition step on price per sqft": round(cond_effect, 2), "effect of one grade step, grade 7 and up": round(grade7_effect, 2),
         "variation in price per sqft explained by grade and condition": round(r2_quality, 2),
         "bought Sep to Nov, sold 6 months later": round(autumn, 2), "bought May to Aug, sold 6 months later": round(midyear, 2)}
for slide, what, text in ON_SLIDES:
    lines.append(f"| `{slide}.tex` | {what} | {text} | {exact.get(what, '')} |")
lines += ["", "## Numbers that are only in pictures", "", "| picture | numbers |", "|---|---|"]
lines += [f"| `{p}` | {t} |" for p, t in IN_PICTURES]
lines += ["", "## Detail for questions (not on the slides)", "",
          f"- Regression of the log price per sqft on condition and grade (lower-priced zipcodes, {len(quality):,} sales), each adjusted for the other.",
          f"- One step of condition: {sp(cond_effect)} per step (95% interval {sp(cond_ci[0])} to {sp(cond_ci[1])}, 2,000 bootstrap resamples). It is an average: the medians are flat from condition 2 to 4 and jump at 5.",
          f"- One step of grade, grade 7 and up: {sp(grade7_effect)} per step (95% interval {sp(grade7_ci[0])} to {sp(grade7_ci[1])}): no clear effect.",
          f"- Grade and condition together explain {r2_quality:.0f}% of the variation in the price per sqft.",
          f"- H3 as worded: spring and summer together (Jun to Aug 2014, Mar to May 2015) vs autumn and winter together (Sep 2014 to Feb 2015): {warm_vs_cold:+.1f}% (95% interval {warm_ci[0]:+.1f} to {warm_ci[1]:+.1f}); spring alone: {spring_vs_cold:+.1f}% ({spring_ci[0]:+.1f} to {spring_ci[1]:+.1f}); summer alone: {summer_vs_cold:+.1f}% ({summer_ci[0]:+.1f} to {summer_ci[1]:+.1f}). Pooled medians of the months, 2,000 bootstrap resamples.",
          f"- Trend check: May 2015 against May 2014, the same month a year apart: {same_month_year_later:+.1f}%. So the spring rise can also be a general price rise.",
          f"- 6-month hold (buy in a month, sell 6 months later), used for the +6% on slides 10 to 11: H3 as a decision rule, bought Sep to Nov and sold 6 months later: {sp(autumn)} (95% interval {sp(autumn_lo)} to {sp(autumn_hi)}). Bought May to Aug: {sp(midyear)} (95% interval {sp(midyear_lo)} to {sp(midyear_hi)}), no clear gain.",
          "- The thin black line on each bar of the H3 chart is its own 95% interval. November's starts below zero, so a single month is uncertain; pooling Sep to Nov gives the interval above.",
          "- Below grade 7 the price per sqft is higher (about $190), but those are small houses, and smaller houses cost more per sqft.", "",
          "## How to read the method", "",
          f"- **Lower-priced zipcode**: the median sale price of the zipcode is among the cheapest {PERCENTILE:.0%} of the {n_zips} zipcodes (at most {money(cutoff)}).",
          "- **H2**: median price per sqft at each condition and each grade, lower-priced zipcodes only; levels with fewer than 30 sales are left out.",
          f"- **H3**: median price per sqft of the lower-priced zipcodes in the month bought against {HOLD} months later; the 95% interval comes from bootstrap resamples. "
          f"With only {n_months} months of data, season and general trend cannot be told apart."]
Path("reports").mkdir(exist_ok=True)
Path("reports/numbers.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
Path("reports/numbers.json").write_text(json.dumps([{"slide": s, "what": w, "text": t} for s, w, t in ON_SLIDES], indent=1), encoding="utf-8")
print("[saved] reports/numbers.md")

# ---------------------------------------------------------------------------------------------
# 2. Check: every number is really written on its slide
# ---------------------------------------------------------------------------------------------
def readable(tex):
    """The text of a slide as a person reads it: no TeX escapes, no \\textbf{...}."""
    tex = tex.replace(r"\$", "$").replace(r"\%", "%")
    tex = re.sub(r"\\textbf\{|\\mbox\{|\\textbullet\\? ?", "", tex)
    return tex.replace("$-$", "-").replace("}", "").replace("{", "")


def slide_path(s):
    return Path("slides") / f"{s}.tex"


wrong = [(s, w, t) for s, w, t in ON_SLIDES if t not in readable(slide_path(s).read_text(encoding="utf-8"))]
if wrong:
    print("\n[check] these numbers are NOT on their slide (update the slide, or the slide is right and the number changed):")
    for s, w, t in wrong:
        print(f"   {slide_path(s)}   {w}:  {t}")
    sys.exit(1)
print(f"[check] all {len(ON_SLIDES)} numbers of the report are on their slides")

# ---------------------------------------------------------------------------------------------
# 3. reports/speaker_notes.txt : what to say, with the time plan
# ---------------------------------------------------------------------------------------------
TALK_MIN, QA_MIN = 10, 2
PLAN = [("Title", 0.25, "Welcome. Erin wants to buy, improve and resell houses fairly. Where should she look?"),
        ("Our client: Erin Robinson", 0.5, "Read the sentence, PAUSE; three titles, PAUSE; then the descriptions (they are our assumptions)."),
        ("One year of house sales in King County", 20/60, "Each dot is a house sold, coloured by price. PAUSE; dark = expensive, yellow = cheaper (south); PAUSE; same county, very different prices."),
        ("The data at a glance", 0.5, f"{n_sales:,} sales, {n_zips} zipcodes; PAUSE; good to know: {n_months_data} months only, medians because of a few very expensive sales."),
        ("Our three hypotheses", 0.5, "Where, what, when: one question each, one bubble per click (PAUSE between)."),
        ("H1: where are the lower-priced zipcodes?", 1.0, f"Dot chart, PAUSE, then map and text: {n_low} of {n_zips} zipcodes, all in the south; none of the {n_north} north of downtown."),
        ("Focus: the lower-priced zipcodes", 0.5, "Box plot, PAUSE, bar chart, PAUSE, text. From here on only these zipcodes. They are much cheaper, and twice as many houses are built to a lower standard (grade 6 or lower): that leads to H2."),
        ("H2: does quality raise the price per sqft?", 1.5, f"Grade chart, PAUSE, text, PAUSE, condition chart, PAUSE, text. Only the best condition pays: condition 5 sells for {money(cond5_median)} per sqft, conditions 2 to 4 for about {money(cond_2_4_typical)} (see the chart). Grade: no extra price from 7 up. Most sales are already grade 7 or higher ({share_grade_7up:.0f}%), few are condition 5 ({share_cond5:.0f}%)."),
        ("The bigger the house, the cheaper each sqft", 0.5, f"Title only, PAUSE, intro and correlation chart, PAUSE, orange headline, sentence and grey comment. Big houses cost more in total but less per sqft: {money(size_small_ppsf)} per sqft under 1,200 sqft, {money(size_big_ppsf)} over 2,500 sqft. Only a lead: to test renovating or splitting we need more data (costs, zoning, permits). If asked: rank correlations are in reports/numbers.md (living area {corr_ppsf['sqft_living']:+.2f}, condition {corr_ppsf['condition']:+.2f} with price per sqft; part of that link is built in, since price per sqft is price divided by living area)."),
        ("H3: are prices higher in spring and summer?", 1.0, f"Title, PAUSE, chart, PAUSE, text. Spring and summer together are about {warm_vs_cold:.0f}% above autumn and winter, but all of it is spring ({spring_vs_cold:.0f}%); summer is level. One year only: May 2015 is also {same_month_year_later:.0f}% above May 2014, so season and trend overlap."),
        ("H3: an example", 0.75, f"The bold part of the line: bought in November at {money(example_buy_price)} per sqft, sold 6 months later in May at {money(example_sell_price)}: {example_change:+.1f}%. Buying Sep to Nov and selling 6 months later gained {sp(autumn)} on average (May to Aug buys: {sp(midyear)})."),
        ("Three insights", 1.0, "Geography, quality, timing: one card per click."),
        ("Advice for Erin", 100/60, "Where, what, when, how: one per click. If asked about social responsibility: buy grade 7 or higher (renovation cannot change the grade) and aim to bring the condition to 5. A comment only: we have no data on renovation costs."),
        ("Assumptions, next steps, questions", QA_MIN, "This slide stays up during the two minutes of questions: assumptions and limits (13 months only, medians, no costs), then possible next steps: big houses are cheaper per sqft (renovate, maybe split: zoning, permits and costs not checked), bargains, more months of data.")]
assert abs(sum(m for _, m, _ in PLAN[:-1]) - TALK_MIN) < 1e-9, "the talk part of the plan must add up to TALK_MIN"
t, notes = 0.0, [f"SPEAKER NOTES: {TALK_MIN} MINUTES OF TALK + {QA_MIN} MINUTES OF QUESTIONS", "=" * 80]
for i, (title, minutes, say) in enumerate(PLAN, 1):
    a, b = round(t * 60), round((t + minutes) * 60)
    notes.append(f"{i:>2}. {a // 60}:{a % 60:02d}-{b // 60}:{b % 60:02d}  {title}\n      {say}")
    t += minutes
Path("reports/speaker_notes.txt").write_text("\n".join(notes) + "\n", encoding="utf-8")
print("[saved] reports/speaker_notes.txt")
