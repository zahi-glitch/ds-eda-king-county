"""Step 3: draw every picture of the talk into images/.

    python src/03_make_images.py

The numbers come from analysis.py (the same ones that 02_make_report.py writes to reports/numbers.md).
Each picture is drawn at the size it has on the slide (figsize = centimetres on the slide / 2.54), so the
text inside it is never shrunk and stays readable. The slides only place the finished PNG files.
"""

import json
import math
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap, LogNorm
from matplotlib.patches import Polygon

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analysis import *          # noqa: E402,F403   (the numbers and tables)

IMG = Path("images")
IMG.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------------------------
# Colours (the same as in slides/preamble.tex).  teal = where, coral = what, violet = when, navy = text
# ---------------------------------------------------------------------------------------------
C_BG, C_INK, C_MUTED = "#FFF8F0", "#264653", "#6b7b82"
C_TEAL, C_TEAL_LIGHT, C_TEAL_PALE = "#2A9D8F", "#A6DBD4", "#D6EBE8"
C_CORAL_DARK, C_CORAL_PALE, C_GRAY, C_CONTEXT = "#B5472F", "#F8DDD3", "#B9BEC0", "#ECE6DD"
C_VIOLET = "#7A5BB0"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": C_MUTED, "axes.labelcolor": C_INK,
                     "xtick.color": C_INK, "ytick.color": C_INK, "text.color": C_INK})


sp = lambda v: f"{v:+.0f}%"                  # +6%


def save(fig, name, dpi=250, folder=IMG):
    fig.savefig(folder / name, dpi=dpi, facecolor=C_BG)
    plt.close(fig)
    print(f"[saved] {folder}/{name}")


def save_split(fig, left_name, right_name, ax_left, ax_right, dpi=250):
    """Save a two-panel figure as two pictures (cut in the gap between the panels) so each panel can appear on its own click.
    Both pictures have the same height and the same panel position, so they line up on the slide. Prints the width of each in cm."""
    import io
    from PIL import Image
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    mid = (ax_left.get_tightbbox(renderer).x1 + ax_right.get_tightbbox(renderer).x0) / 2 / (fig.get_figwidth() * fig.dpi)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, facecolor=C_BG)
    plt.close(fig)
    img = Image.open(buf)
    cut = round(img.width * mid)
    img.crop((0, 0, cut, img.height)).save(IMG / left_name)
    img.crop((cut, 0, img.width, img.height)).save(IMG / right_name)
    width_cm = img.width / dpi * 2.54
    print(f"[saved] {IMG}/{left_name} ({width_cm * mid:.2f} cm) and {right_name} ({width_cm * (1 - mid):.2f} cm)")


def clean(ax):
    """Axes without the top and right line, on the slide background."""
    ax.set_facecolor(C_BG)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)


# ---------------------------------------------------------------------------------------------
# Zipcode shapes (data/raw/wa_zip_codes.geojson)
# ---------------------------------------------------------------------------------------------
with open("data/raw/wa_zip_codes.geojson", encoding="utf-8") as f:
    features = [ft for ft in json.load(f)["features"] if ft["properties"]["ZCTA5CE10"] in set(zips.index)]


def rings(geometry):
    if geometry["type"] == "Polygon":
        return [geometry["coordinates"][0]]
    return [poly[0] for poly in geometry["coordinates"]]


def bbox_of(zip_list, margin):
    h = houses[houses["zipcode"].isin(zip_list)]
    return h["long"].min() - margin, h["long"].max() + margin, h["lat"].min() - margin, h["lat"].max() + margin


def zipcode_map(name, zip_list, fills, width_cm, margin=0.03):
    """Zipcodes of zip_list fill the picture (coloured as in `fills`); the others stay light grey for orientation."""
    x0, x1, y0, y1 = bbox_of(zip_list, margin)
    aspect = ((x1 - x0) * math.cos(math.radians((y0 + y1) / 2))) / (y1 - y0)
    fig = plt.figure(figsize=(width_cm / 2.54, width_cm / 2.54 / aspect), facecolor=C_BG)
    ax = fig.add_axes([0, 0, 1, 1])
    for ft in features:
        z = ft["properties"]["ZCTA5CE10"]
        for ring in rings(ft["geometry"]):
            ax.add_patch(Polygon(ring, closed=True, facecolor=fills.get(z, C_CONTEXT), edgecolor="white", linewidth=0.8))
    ax.set_xlim(x0, x1)
    ax.set_ylim(y0, y1)
    ax.axis("off")
    save(fig, name)
    print(f"        size on the slide: {width_cm:.2f} x {width_cm / aspect:.2f} cm")


# ---------------------------------------------------------------------------------------------
# Slide 3: every house, coloured by price, with the sea and lakes in light blue
# ---------------------------------------------------------------------------------------------
def water_layer(x0, x1, y0, y1, px=1800):
    """Light blue for the sea and the lakes: everything in the frame that no zipcode covers and that is either
    connected to the west edge (Puget Sound) or enclosed by land (lakes). Land outside the county stays empty."""
    from PIL import Image, ImageDraw
    from scipy import ndimage as ndi
    ph = int(px * (y1 - y0) / ((x1 - x0) * math.cos(math.radians((y0 + y1) / 2))))
    img = Image.new("L", (px, ph), 0)
    dr = ImageDraw.Draw(img)
    for ft in features:
        for ring in rings(ft["geometry"]):
            dr.polygon([((lo - x0) / (x1 - x0) * px, (y1 - la) / (y1 - y0) * ph) for lo, la in ring], fill=1)
    land = ndi.binary_closing(np.asarray(img) > 0, structure=np.ones((3, 3)), iterations=2)   # seal the hairlines between zipcodes
    lab, _ = ndi.label(~land)
    keep = np.zeros_like(land)
    for i, sl in enumerate(ndi.find_objects(lab), 1):
        part = lab[sl] == i
        if part.sum() < 400:
            continue
        touches_left = sl[1].start == 0
        touches_other = sl[0].start == 0 or sl[0].stop == ph or sl[1].stop == px
        if touches_left or not touches_other:
            keep[sl] |= part
    keep = ndi.binary_opening(keep, structure=np.ones((3, 3)))
    rgba = np.zeros((ph, px, 4), dtype=float)
    rgba[keep] = (0.80, 0.90, 0.96, 1.0)
    return rgba


def price_map():
    price_cmap = LinearSegmentedColormap.from_list("price", ["#F6CB5E", "#EE8F4B", "#D2503C", "#264653"])   # yellow -> navy
    x0, x1, y0, y1 = bbox_of(list(zips.index), 0.0)
    x0 -= 0.02                                                      # a little sea on the west side only
    aspect = ((x1 - x0) * math.cos(math.radians((y0 + y1) / 2))) / (y1 - y0)
    W, H = 16.0, 6.45                                               # the picture: the whole width of the slide, in cm
    map_h = H - 0.2
    map_w = map_h * aspect
    left, bar_gap, bar_w, bar_h, bar_y = 0.25, 0.7, 0.34, H - 2.5, 0.9
    fig = plt.figure(figsize=(W / 2.54, H / 2.54), facecolor=C_BG)
    ax = fig.add_axes([left / W, 0.1 / H, map_w / W, map_h / H])
    ax.imshow(water_layer(x0, x1, y0, y1), extent=(x0, x1, y0, y1), origin="upper", aspect="auto", zorder=0, interpolation="bilinear")
    for ft in features:
        for ring in rings(ft["geometry"]):
            ax.add_patch(Polygon(ring, closed=True, facecolor="#F1EBE1", edgecolor="white", linewidth=0.4, zorder=1))
    h = houses.dropna(subset=["price"]).sort_values("price")        # dark dots on top
    dots = ax.scatter(h["long"], h["lat"], c=h["price"].clip(upper=1_500_000), cmap=price_cmap,
                      norm=LogNorm(vmin=150_000, vmax=1_500_000), s=2.2, linewidths=0, alpha=0.95, zorder=3)
    ax.set_xlim(x0, x1)
    ax.set_ylim(y0, y1)
    ax.axis("off")
    cax = fig.add_axes([(left + map_w + bar_gap) / W, bar_y / H, bar_w / W, bar_h / H])
    cb = fig.colorbar(dots, cax=cax, extend="max")
    cb.set_ticks([200_000, 300_000, 450_000, 700_000, 1_000_000, 1_500_000])
    cb.set_ticklabels(["\\$200k", "\\$300k", "\\$450k", "\\$700k", "\\$1M", "\\$1.5M+"])
    cb.ax.tick_params(labelsize=10, colors=C_INK, length=2)
    cb.outline.set_visible(False)
    cb.ax.minorticks_off()
    fig.text((left + map_w + bar_gap) / W, (bar_y + bar_h + 0.55) / H, "Sale price", fontsize=11, fontweight="bold", color=C_INK, ha="left")
    save(fig, "pres_price_map.png", dpi=300)
    print(f"        colour bar: x = {left + map_w + bar_gap:.2f} cm, from {bar_y:.2f} to {bar_y + bar_h:.2f} cm above the bottom of the {H} cm picture")


# ---------------------------------------------------------------------------------------------
# Slide 4: histogram of the sale prices (9.2 x 4.4 cm on the slide)
# ---------------------------------------------------------------------------------------------
def price_histogram():
    fig, ax = plt.subplots(figsize=(10.6 / 2.54, 5.0 / 2.54), facecolor=C_BG)
    clean(ax)
    p = sold["price"]
    ax.hist(p[p <= price_cap] / 1000, bins=np.arange(0, 1525, 50), color=C_GRAY, edgecolor=C_BG, lw=0.6)
    ax.axvline(county_median / 1000, color=C_INK, lw=1.6)
    ax.text(county_median / 1000 + 25, ax.get_ylim()[1] * 0.95, f"median \\${county_median:,.0f}", fontsize=10, color=C_INK, va="top", fontweight="bold")
    ax.text(0.99, 0.55, f"{n_above_cap} sales above \\$1.5M\nnot shown", transform=ax.transAxes, ha="right", fontsize=9, color=C_MUTED)
    ax.set_xlabel("Sale price ($ thousand)", fontsize=10)
    ax.set_ylabel("Sales", fontsize=10)
    ax.tick_params(labelsize=9)
    fig.tight_layout()
    save(fig, "pres_prices.png")


# ---------------------------------------------------------------------------------------------
# Slide 6: the whole county, lower-priced zipcodes in teal
# ---------------------------------------------------------------------------------------------
def county_map():
    zipcode_map("pres_county_low.png", list(zips.index), {z: C_TEAL for z in low_set}, width_cm=7.2)
    # one dot per zipcode: median price against latitude (south to north), with the 25th percentile limit
    is_low = zip_lat.index.isin(low_set)
    fig, ax = plt.subplots(figsize=(8.1 / 2.54, 5.9 / 2.54), facecolor=C_BG)
    clean(ax)
    ax.axhline(cutoff / 1000, color=C_TEAL, lw=1.2, ls="--", zorder=1, label=f"25th percentile: ${cutoff / 1000:.0f}k".replace("$", "\\$"))
    ax.scatter(zip_lat.loc[~is_low, "lat"], zip_lat.loc[~is_low, "price"] / 1000, s=30, color=C_GRAY, edgecolor="white", lw=0.6, zorder=3, label="Other zipcodes")
    ax.scatter(zip_lat.loc[is_low, "lat"], zip_lat.loc[is_low, "price"] / 1000, s=36, color=C_TEAL, edgecolor="white", lw=0.6, zorder=4, label=f"Lower-priced ({n_low})")
    ax.set_yscale("log")
    ax.set_ylim(190, 4200)
    ax.set_yticks([250, 500, 1000, 2000])
    ax.set_yticklabels(["250", "500", "1,000", "2,000"])
    ax.minorticks_off()
    ax.set_xlabel("South  \u2190  latitude  \u2192  North", fontsize=10)
    ax.set_title("Zipcode median price ($ thousand)".replace("$", "\\$"), fontsize=10.5, loc="left", color=C_INK, fontweight="bold")
    ax.tick_params(labelsize=9.5)
    ax.set_xticks([])
    ax.legend(frameon=False, fontsize=9.5, loc="upper left", handletextpad=0.2, borderaxespad=0.2)
    fig.tight_layout()
    save(fig, "pres_south.png")


# ---------------------------------------------------------------------------------------------
# Slide 7: the lower-priced zipcodes and how they compare with the others (boxes of the sale prices, share of lower-grade sales)
# ---------------------------------------------------------------------------------------------
def focus_pictures():
    """Left: how the sale prices are spread (box = middle half of the sales, line = median, whiskers = 5% to 95%). Right: share of lower-grade sales."""
    labels = ["Lower-priced\nzipcodes", "Other\nzipcodes"]
    fig, (axp, axg) = plt.subplots(1, 2, figsize=(13.4 / 2.54, 5.4 / 2.54), facecolor=C_BG, gridspec_kw={"width_ratios": [1.15, 1]})
    # --- boxes of the sale prices
    clean(axp)
    data = [low["price"].to_numpy() / 1000, rest["price"].to_numpy() / 1000]
    bp = axp.boxplot(data, widths=0.52, whis=(5, 95), showfliers=False, patch_artist=True, positions=[0, 1],
                     medianprops=dict(color=C_INK, lw=2.4), whiskerprops=dict(color=C_MUTED, lw=1.2), capprops=dict(color=C_MUTED, lw=1.2))
    for patch, colour in zip(bp["boxes"], [C_TEAL, C_GRAY]):
        patch.set(facecolor=colour, edgecolor="none")
    for x, med in ((0, low_median / 1000), (1, rest_median / 1000)):
        axp.text(x + 0.36, med, f"{med:.0f}", ha="left", va="center", fontsize=10.5, fontweight="bold", color=C_INK)
    axp.set_xlim(-0.55, 1.85)
    axp.set_ylim(0, max(np.percentile(d, 95) for d in data) * 1.06)
    axp.set_xticks([0, 1]); axp.set_xticklabels(labels, fontsize=9)
    axp.tick_params(axis="y", labelsize=8.5)
    axp.set_title("Sale price ($ thousand)".replace("$", "\\$"), fontsize=9.5, loc="left", color=C_INK, fontweight="bold")
    # --- share of lower-grade sales
    clean(axg)
    axg.bar([0, 1], [plain_low, plain_rest], width=0.62, color=[C_TEAL, C_GRAY])
    for x, v in ((0, plain_low), (1, plain_rest)):
        axg.text(x, v + 0.5, f"{v:.0f}%", ha="center", fontsize=11, fontweight="bold", color=C_INK)
    axg.set_ylim(0, max(plain_low, plain_rest) * 1.2)
    axg.set_title(r"$\mathtt{grade}$ 6 or lower (% of sales)", fontsize=9.5, loc="left", color=C_INK, fontweight="bold")
    axg.set_xticks([0, 1]); axg.set_xticklabels(labels, fontsize=9)
    axg.set_yticks([]); axg.spines["left"].set_visible(False)
    fig.tight_layout(w_pad=2.0)
    save_split(fig, "pres_focus_prices.png", "pres_focus_grade.png", axp, axg)


# ---------------------------------------------------------------------------------------------
# Slide 8: median price per sqft by grade (left) and by condition (right) (15.2 x 5.9 cm)
# ---------------------------------------------------------------------------------------------
def quality_lines():
    def lines(ax, table, labels, title, ylabel=False):
        clean(ax)
        table = table[table["n"] >= MIN_SALES]                 # levels with fewer sales are left out
        xs = list(range(len(table)))
        ax.plot(xs, table["median"], color=C_CORAL_DARK, lw=2.5, marker="o", ms=7, zorder=3)
        for x, m in zip(xs, table["median"]):
            ax.text(x, m + 9, f"{m:.0f}", ha="center", fontsize=10.5, fontweight="bold", color=C_INK)
        ax.set_xticks(xs)
        ax.set_xticklabels([labels.get(i, str(i)) for i in table.index], fontsize=10)
        ax.set_title(title, fontsize=11, loc="left", color=C_INK, fontweight="bold")
        ax.set_ylim(120, 225)
        ax.set_xlim(-0.5, len(table) - 0.5)
        ax.tick_params(axis="y", labelsize=9)
        if ylabel:
            ax.set_ylabel("Median \\$ per sqft", fontsize=9)
        return table

    fig, (axg, axc) = plt.subplots(1, 2, figsize=(15.2 / 2.54, 5.9 / 2.54), facecolor=C_BG, sharey=True)   # grade first (left), then condition
    gt = lines(axg, grade_table, {"5-": "\u22645", "10+": "10+"}, r"$\mathtt{grade}$ (how well it was built)", ylabel=True)
    lines(axc, cond_table, {5: "5 good"}, r"$\mathtt{condition}$ (upkeep today)")
    first7 = list(gt.index).index("7")                         # grade 7 and above: the price per sqft stays flat
    axg.axvspan(first7 - 0.5, len(gt) - 0.5, color=C_CORAL_PALE, alpha=0.8, lw=0, zorder=0)
    axg.text((first7 + len(gt) - 1) / 2, 213, "ours: flat from 7 up", ha="center", fontsize=10, color=C_CORAL_DARK, style="italic")
    # grade 6 or lower: we do not buy these (responsible choice, and the grade cannot be improved), so they are drawn in grey
    gray = "#8A949A"
    axg.plot(range(first7), gt["median"].to_numpy()[:first7], color=gray, lw=2.5, marker="o", ms=7, zorder=4)
    for t in axg.texts[:first7]:
        t.set_color(gray)
    axg.text((first7 - 1) / 2 - 0.1, 168, "we avoid\nthese", ha="center", va="top", fontsize=9.5, color=gray, style="italic")
    fig.tight_layout(w_pad=1.2)
    save_split(fig, "pres_quality_grade.png", "pres_quality_condition.png", axg, axc)


# ---------------------------------------------------------------------------------------------
# Slide 9: which columns go with the price per sqft (rank correlation, lower-priced zipcodes), 12.0 x 3.8 cm
# ---------------------------------------------------------------------------------------------
def corr_chart(name="pres_corr.png"):
    """Slide 9, big picture in the middle: what goes with the price per sqft (rank correlation with each other column), lower-priced zipcodes. 12.0 x 3.8 cm, no title (the slide has the intro above and the orange headline below)."""
    fig, axl = plt.subplots(figsize=(12.0 / 2.54, 3.8 / 2.54), facecolor=C_BG)
    clean(axl)
    corr = corr_ppsf.sort_values(ascending=False)                 # strongest positive first, living area (most negative) at the bottom
    names = list(corr.index)                                      # the column names of the data, written like code
    ys = list(range(len(corr)))
    colours = [C_CORAL_DARK if c == "sqft_living" else "#B9C0C4" for c in corr.index]
    axl.barh(ys, corr.to_numpy(), color=colours, height=0.68, zorder=2)
    axl.axvline(0, color=C_MUTED, lw=1)
    for y, v, c in zip(ys, corr.to_numpy(), corr.index):
        axl.text(v + (0.02 if v >= 0 else -0.02), y, f"{v:+.2f}".replace("-", "\u2212"), ha="left" if v >= 0 else "right", va="center", fontsize=9,
                 fontweight="bold" if c == "sqft_living" else "normal", color=C_INK)
    axl.set_yticks(ys); axl.set_yticklabels(names, fontsize=8.5, fontfamily="monospace")
    axl.set_xlim(-0.75, 0.40)
    axl.set_xticks([])
    axl.invert_yaxis()
    axl.spines["left"].set_visible(False); axl.spines["bottom"].set_visible(False)
    axl.tick_params(length=0)
    # direction hints in the two empty corners (the positive bars are at the top, the negative ones below)
    axl.text(-0.04, 1, "\u2190 cheaper per sqft", ha="right", va="center", fontsize=8.5, color=C_MUTED, style="italic")
    axl.text(0.04, 4, "dearer per sqft \u2192", ha="left", va="center", fontsize=8.5, color=C_MUTED, style="italic")
    fig.tight_layout()
    save(fig, name)


# ---------------------------------------------------------------------------------------------
# Slides 10 and 11: median price per sqft of each month, with the four seasons (15.2 x 5.0 cm)
# ---------------------------------------------------------------------------------------------
def when_chart(name="pres_when.png", with_example=False):
    """Median price per sqft of each month (13 months). The four seasons are shaded (warm = violet, cold = grey) and labelled with the
    median of their three months. Violet dots = the months H3 is about (spring and summer). Drawn at 15.2 x 5.0 cm.
    with_example=True (slide 11) marks the two dots of the example (bought in November, sold 6 months later) and drops the dollar labels of the bands."""
    months = list(month_median.index)
    values = month_median.to_numpy()
    n = len(months)
    fig, ax = plt.subplots(figsize=(15.2 / 2.54, 5.0 / 2.54), facecolor=C_BG)
    clean(ax)
    shade = {"Summer": "#E4DCF1", "Autumn": "#ECE8E1", "Winter": "#E1DDD5", "Spring": "#CFC2E7"}   # warm seasons violet, cold seasons grey
    ymax = 194
    in_band = np.zeros(n, dtype=bool)
    for season, (first, last) in SEASONS.items():
        i0, i1 = months.index(pd.Period(first)), months.index(pd.Period(last))
        ax.axvspan(i0 - 0.5, i1 + 0.5, color=shade[season], lw=0)
        ax.text((i0 + i1) / 2, ymax - 1, season if with_example else f"{season}\n\\${season_median[season]:.0f}", ha="center", va="top", fontsize=11, fontweight="bold", color=C_INK)
        in_band[i0:i1 + 1] = season in WARM
    winter = cold_median                                                                  # the level of autumn and winter together
    ax.axhline(winter, color=C_MUTED, lw=1, ls="--", zorder=1)                            # the autumn and winter level, to compare with
    ax.plot(range(n), values, color=C_MUTED, lw=1.8, zorder=2)
    ax.scatter(range(n), values, s=34, zorder=3, color=[C_VIOLET if m else "#8A949A" for m in in_band], edgecolor=C_BG, linewidths=0.8)
    if with_example:                                                   # ONE example: bought in Nov 2014, sold 6 months later (May 2015): just those two dots, dark
        buy = months.index(EXAMPLE_BUY)
        sell = buy + HOLD
        ax.scatter([buy, sell], values[[buy, sell]], s=85, zorder=4, color=C_INK, edgecolor=C_BG, linewidths=0.8)
    ax.set_xticks(range(n))
    ax.set_xticklabels([m.strftime("%b") + (f"\n{m.year}" if (k == 0 or m.month == 1) else "") for k, m in enumerate(months)], fontsize=9.5)
    ax.set_xlim(-0.5, n - 0.5)
    ax.set_ylim(148, ymax)
    ax.set_yticks([150, 160, 170, 180])
    ax.tick_params(axis="y", labelsize=9.5)
    ax.set_ylabel("\\$ per sqft", fontsize=9.5)
    ax.set_title("Median price per sqft by month of sale", fontsize=12, loc="left", color=C_INK, fontweight="bold")
    fig.tight_layout()
    save(fig, name)


if __name__ == "__main__":
    price_map()                                     # slide 3
    price_histogram()                               # slide 4
    county_map()                                    # slide 6
    focus_pictures()                                # slide 7
    quality_lines()                                 # slide 8
    corr_chart()                                    # slide 9
    when_chart()                                    # slide 10
    when_chart(name="pres_when_example.png", with_example=True)   # slide 11
