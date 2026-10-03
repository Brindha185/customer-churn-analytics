"""
build_dashboards.py
-------------------
Generates the three project dashboards as ready-to-use PNG images from YOUR data:

  screenshots/dashboard_1_executive.png
  screenshots/dashboard_2_segmentation.png
  screenshots/dashboard_3_risk.png

Input : data/cleaned/churn_features.csv  (created by run_all.py / run_sql.py)
Every number, chart and recommendation is computed from the data at run time. Nothing is hard-coded.
Recommendation bullets only appear when the data supports them.

Usage:  python python/build_dashboards.py
Needs:  pip install matplotlib
"""
import sys
import textwrap
from pathlib import Path

import numpy as np
import pandas as pd

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap
    from matplotlib.patches import FancyBboxPatch
except ImportError:
    sys.exit("matplotlib is not installed. Run:  pip install matplotlib")

ROOT = Path(__file__).resolve().parents[1]

RED, BLUE, NAVY = "#C0392B", "#2E75B6", "#1F3864"
GREY, LIGHT, DARK = "#8C8C8C", "#F2F2F2", "#404040"
AMBER, LBLUE = "#E0A030", "#9DC3E6"
TENURE_ORDER = ["0-6 mo", "7-12 mo", "13-24 mo", "25-48 mo", "49-72 mo"]
FIGSIZE, DPI = (16, 10.5), 120
SOURCE = ("Source: IBM Telco Customer Churn sample dataset (fictional). Single snapshot; no calendar dates. "
          "Rates show churned customers / all customers in the file.")

plt.rcParams.update({"font.family": "DejaVu Sans", "axes.facecolor": "white", "figure.facecolor": "white"})
WHITE_RED = LinearSegmentedColormap.from_list("w2r", ["#FFFFFF", "#E8837A", RED])


# ---------------------------------------------------------------- helpers
def pct(x, d=1):
    return f"{x * 100:.{d}f}%"


def seg_table(df, col, order=None):
    g = df.groupby(col).agg(n=("churn_flag", "size"), churned=("churn_flag", "sum"), rate=("churn_flag", "mean"))
    if order is not None:
        g = g.reindex([o for o in order if o in g.index])
    return g


def clean_ax(ax):
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(length=0)


def title_ax(ax, title, sub=None, width=60):
    lines = textwrap.wrap(sub, width) if sub else []
    ax.set_title(title, loc="left", fontsize=11.5, fontweight="bold", color=NAVY, pad=10 + 10.5 * len(lines))
    if lines:
        ax.text(0, 1.015, "\n".join(lines), transform=ax.transAxes, fontsize=8.1, color=GREY, va="bottom",
                linespacing=1.25)


def hi_lo(tbl):
    top, low = tbl["rate"].idxmax(), tbl["rate"].idxmin()
    return f"Highest: {top} ({pct(tbl.loc[top, 'rate'])}). Lowest: {low} ({pct(tbl.loc[low, 'rate'])})."


def hbar(ax, tbl, overall, title, sub=None, color=RED):
    y = np.arange(len(tbl))
    ax.barh(y, tbl["rate"], color=color, height=0.62)
    ax.set_yticks(y)
    ax.set_yticklabels([str(i) for i in tbl.index], fontsize=9)
    xm = max(tbl["rate"].max(), overall) * 1.45
    ax.set_xlim(0, xm)
    ax.set_ylim(len(tbl) - 0.4, -1.0)
    ax.axvline(overall, color=DARK, ls="--", lw=1)
    ax.text(overall, -0.72, f"overall {pct(overall)}", fontsize=7.5, ha="center", color=DARK)
    for yi, (r, n) in enumerate(zip(tbl["rate"], tbl["n"])):
        ax.text(r + xm * 0.012, yi, f"{pct(r)}  (n={n:,})", va="center", fontsize=8.5, color=DARK)
    ax.set_xticks([])
    clean_ax(ax)
    title_ax(ax, title, sub)


def vbar(ax, tbl, overall, title, sub=None, color=RED, rot=0, labels=None):
    x = np.arange(len(tbl))
    ax.bar(x, tbl["rate"], color=color, width=0.62)
    ax.set_xticks(x)
    ax.set_xticklabels(labels or [str(i) for i in tbl.index], fontsize=8.5, rotation=rot,
                       ha="right" if rot else "center")
    ym = max(tbl["rate"].max(), overall) * 1.25
    ax.set_ylim(0, ym)
    ax.axhline(overall, color=DARK, ls="--", lw=1)
    sub = (sub + "  |  " if sub else "") + f"dashed line = overall {pct(overall)}"
    for xi, (r, n) in enumerate(zip(tbl["rate"], tbl["n"])):
        ax.text(xi, r + ym * 0.015, f"{pct(r)}\nn={n:,}", ha="center", va="bottom", fontsize=8, color=DARK,
                bbox=dict(fc="white", ec="none", pad=1.2, alpha=0.85))
    ax.set_yticks([])
    clean_ax(ax)
    title_ax(ax, title, sub)


def heatmap(ax, rate, n, title, sub=None):
    vals = rate.values.astype(float)
    vmax = np.nanmax(vals) if np.isfinite(vals).any() else 1
    ax.imshow(np.ma.masked_invalid(vals), cmap=WHITE_RED, vmin=0, vmax=vmax, aspect="auto")
    ax.set_xticks(range(rate.shape[1]))
    ax.set_xticklabels([str(c) for c in rate.columns], fontsize=8.5)
    ax.set_yticks(range(rate.shape[0]))
    ax.set_yticklabels([str(i) for i in rate.index], fontsize=9)
    for i in range(rate.shape[0]):
        for j in range(rate.shape[1]):
            v, c = vals[i, j], n.values[i, j]
            if np.isfinite(v) and c > 0:
                ax.text(j, i, f"{pct(v, 0)}\nn={int(c):,}", ha="center", va="center", fontsize=8,
                        color="white" if v > vmax * 0.65 else DARK)
            else:
                ax.text(j, i, "-", ha="center", va="center", fontsize=9, color=GREY)
    ax.xaxis.tick_top()
    clean_ax(ax)
    lines = textwrap.wrap(sub, 50) if sub else []
    ax.set_title(title, loc="left", fontsize=11.5, fontweight="bold", color=NAVY, pad=30 + 10.5 * len(lines))
    if lines:
        ax.text(0, 1.11, "\n".join(lines), transform=ax.transAxes, fontsize=8.1, color=GREY, va="bottom",
                linespacing=1.25)


def kpi_card(fig, rect, label, value, accent=NAVY):
    ax = fig.add_axes(rect)
    ax.set_axis_off()
    ax.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0,rounding_size=0.06",
                                fc=LIGHT, ec="#D9D9D9", transform=ax.transAxes))
    ax.text(0.5, 0.74, label, ha="center", va="center", fontsize=10, color=GREY, transform=ax.transAxes)
    ax.text(0.5, 0.35, value, ha="center", va="center", fontsize=22, fontweight="bold", color=accent,
            transform=ax.transAxes)


def frame(fig, title, page):
    fig.text(0.04, 0.955, title, fontsize=21, fontweight="bold", color=NAVY, va="center")
    names = ["1  Overview", "2  Segmentation", "3  Retention & Risk"]
    x = 0.96
    for i in range(2, -1, -1):
        fig.text(x, 0.955, names[i], fontsize=10, ha="right", va="center",
                 fontweight="bold" if i + 1 == page else "normal", color=NAVY if i + 1 == page else GREY)
        x -= 0.115 if i != 2 else 0.14
    fig.add_artist(plt.Line2D([0.04, 0.96], [0.925, 0.925], color="#D9D9D9", lw=1))
    fig.text(0.04, 0.018, SOURCE, fontsize=7.8, color=GREY, va="center")


# ---------------------------------------------------------------- data prep
def prepare(df):
    df = df.copy()
    df["risk_segment"] = np.where(df.churn_flag == 1, "Churned",
                          np.where(df.high_risk_flag == 1, "High risk",
                          np.where(df.contract == "Month-to-month", "Watch", "Stable")))
    return df


def driver_table(df, overall):
    attrs = {"contract": "Contract", "internet_service": "Internet", "payment_method": "Payment",
             "paperless_billing": "Paperless billing", "tech_support": "Tech Support",
             "online_security": "Online Security", "online_backup": "Online Backup",
             "device_protection": "Device Protection", "streaming_tv": "Streaming TV",
             "streaming_movies": "Streaming Movies", "senior_citizen": "Senior",
             "partner": "Partner", "dependents": "Dependents"}
    rows = []
    for col, nice in attrs.items():
        if col not in df.columns:
            continue
        g = df.groupby(col).agg(n=("churn_flag", "size"), rate=("churn_flag", "mean"))
        for val, r in g.iterrows():
            if r.n >= 100:
                rows.append({"label": f"{nice}: {val}", "n": int(r.n), "rate": r.rate, "gap": r.rate - overall})
    d = pd.DataFrame(rows)
    d["abs"] = d["gap"].abs()
    return d.sort_values("abs", ascending=False).head(12).sort_values("gap", ascending=False)


# ---------------------------------------------------------------- dashboards
def dashboard_1(df, out):
    overall = df.churn_flag.mean()
    fig = plt.figure(figsize=FIGSIZE, dpi=DPI)
    frame(fig, "Customer Churn & Retention: Executive Overview", 1)

    total, churned = len(df), int(df.churn_flag.sum())
    cards = [("Total Customers", f"{total:,}", NAVY), ("Churn Rate", pct(overall, 2), RED),
             ("Retention Rate", pct(1 - overall, 2), BLUE),
             ("Monthly Revenue Lost", f"${df.loc[df.churn_flag == 1, 'monthly_charges'].sum():,.0f}", RED),
             ("Active Customers", f"{total - churned:,}", NAVY)]
    for i, (lab, val, col) in enumerate(cards):
        kpi_card(fig, [0.04 + i * 0.1845, 0.78, 0.1695, 0.115], lab, val, col)

    ct = seg_table(df, "contract").sort_values("rate", ascending=False)
    hbar(fig.add_axes([0.125, 0.475, 0.255, 0.20]), ct, overall, "Churn rate by contract type",
         "Does commitment length matter?")

    lc = df.assign(b=((df.tenure_months.clip(lower=1) - 1) // 6) * 6 + 1)
    lt = lc.groupby("b").agg(n=("churn_flag", "size"), rate=("churn_flag", "mean"))
    ax = fig.add_axes([0.47, 0.475, 0.49, 0.20])
    ax.plot(range(len(lt)), lt.rate, color=RED, lw=2.2, marker="o", ms=5)
    ax.axhline(overall, color=DARK, ls="--", lw=1)
    ax.set_xticks(range(len(lt)))
    ax.set_xticklabels([f"{b}-{b + 5}\nn={int(n):,}" for b, n in zip(lt.index, lt.n)], fontsize=7.6)
    for i, r in enumerate(lt.rate):
        ax.text(i, r + 0.012, pct(r, 0), ha="center", fontsize=8, color=DARK)
    ax.set_ylim(0, lt.rate.max() * 1.25)
    ax.set_yticks([])
    clean_ax(ax)
    title_ax(ax, "Churn rate by months since signup (lifecycle view)",
             f"No dates in this dataset: customer age, not a calendar trend. X = months since signup. Dashed = overall {pct(overall)}")

    city = seg_table(df, "city")
    city = city[city.n >= 30].sort_values("rate", ascending=False).head(15)
    ax = fig.add_axes([0.06, 0.115, 0.90, 0.225])
    if len(city):
        vbar(ax, city, overall, "Churn rate by city (top 15 by churn rate, cities with 30+ customers)",
             "California only; small cities swing widely, so read each rate together with its n", rot=30)
    fig.savefig(out, dpi=DPI)
    plt.close(fig)


def dashboard_2(df, out):
    overall = df.churn_flag.mean()
    fig = plt.figure(figsize=FIGSIZE, dpi=DPI)
    frame(fig, "Customer Segmentation", 2)

    # row 1
    hh = seg_table(df, "household_type").sort_values("rate", ascending=False)
    hbar(fig.add_axes([0.16, 0.53, 0.20, 0.27]), hh, overall, "Household type (age substitute)", hi_lo(hh))

    tn = seg_table(df, "tenure_group", TENURE_ORDER)
    vbar(fig.add_axes([0.45, 0.53, 0.22, 0.27]), tn, overall, "Churn by tenure group", hi_lo(tn))

    inet_order = [i for i in ["DSL", "Fiber optic", "No"] if i in set(df.internet_service)]
    r = df.pivot_table(index="internet_service", columns="services_count", values="churn_flag", aggfunc="mean").reindex(inet_order)
    c = df.pivot_table(index="internet_service", columns="services_count", values="churn_flag", aggfunc="size").reindex(inet_order).fillna(0)
    heatmap(fig.add_axes([0.765, 0.53, 0.20, 0.24]), r, c, "Internet type x add-ons",
            "Plan proxy: does churn fall with more add-ons?")

    # row 2
    pm = (df.groupby(["payment_method", "contract_category"]).churn_flag.agg(["mean", "size"]).reset_index())
    methods = df.groupby("payment_method").churn_flag.mean().sort_values(ascending=False).index.tolist()
    ax = fig.add_axes([0.16, 0.09, 0.20, 0.27])
    h = 0.36
    for k, (cat, col) in enumerate([("Month-to-month", RED), ("Long-term", BLUE)]):
        sub = pm[pm.contract_category == cat].set_index("payment_method").reindex(methods)
        y = np.arange(len(methods)) + (k - 0.5) * h
        ax.barh(y, sub["mean"].fillna(0), height=h, color=col, label=cat)
        for yi, (v, n) in zip(y, zip(sub["mean"], sub["size"])):
            if pd.notna(v):
                ax.text(v + 0.006, yi, f"{pct(v, 0)} (n={int(n):,})", va="center", fontsize=7.6, color=DARK)
    ax.set_yticks(range(len(methods)))
    ax.set_yticklabels(methods, fontsize=8.5)
    ax.set_ylim(len(methods) - 0.4, -0.9)
    ax.axvline(overall, color=DARK, ls="--", lw=1)
    ax.set_xlim(0, max(pm["mean"].max(), overall) * 1.6)
    ax.set_xticks([])
    ax.legend(fontsize=8, frameon=False, loc="lower right")
    clean_ax(ax)
    title_ax(ax, "Payment method, within each contract type",
             "Does payment method matter once contract is held fixed?")

    vs = seg_table(df, "value_segment", ["Low", "Mid", "High"])
    vbar(fig.add_axes([0.45, 0.09, 0.22, 0.27]), vs, overall, "Churn by customer value (CLTV quartiles)",
         "CLTV is modelled by IBM. Low = bottom 25%, High = top 25%")

    r = df.pivot_table(index="contract_category", columns="tenure_group", values="churn_flag", aggfunc="mean").reindex(columns=TENURE_ORDER)
    c = df.pivot_table(index="contract_category", columns="tenure_group", values="churn_flag", aggfunc="size").reindex(columns=TENURE_ORDER).fillna(0)
    heatmap(fig.add_axes([0.765, 0.09, 0.20, 0.22]), r, c, "Contract x tenure",
            "Where two factors combine. Darker = higher churn rate.")
    fig.savefig(out, dpi=DPI)
    plt.close(fig)


def recommendations(df, overall):
    recs = []
    m2m = df[df.contract == "Month-to-month"]
    lt = df[df.contract != "Month-to-month"]
    n_hr = int(df.high_risk_flag.sum())
    if len(m2m) and len(lt) and m2m.churn_flag.mean() > 1.5 * lt.churn_flag.mean():
        recs.append(f"Contract: month-to-month customers churn at {pct(m2m.churn_flag.mean())} (n={len(m2m):,}) vs "
                    f"{pct(lt.churn_flag.mean())} for one- and two-year plans (n={len(lt):,}). Test an incentive to move "
                    f"the {n_hr:,} high-risk month-to-month customers onto a 1-year contract.")
    fy = df[df.tenure_months <= 12]
    if len(fy) and df.churn_flag.sum() > 0:
        share = fy.churn_flag.sum() / df.churn_flag.sum()
        first6 = df[df.tenure_months <= 6].churn_flag.mean()
        if first6 > overall:
            recs.append(f"Onboarding: {pct(share, 0)} of all churners leave within 12 months, and the first 6 months churn "
                        f"at {pct(first6)} vs {pct(overall)} overall. Pilot structured onboarding in the first 90 days.")
    prof = df[df.risk_profile_match == 1]
    if len(prof) and prof.churn_flag.mean() > 1.5 * overall:
        rev = df.loc[df.high_risk_flag == 1, "monthly_charges"].sum()
        cap = prof.churn_flag.sum() / df.churn_flag.sum()
        recs.append(f"Priority list: the risk profile churns at {pct(prof.churn_flag.mean())} ({prof.churn_flag.mean() / overall:.1f}x overall) "
                    f"but captures only {pct(cap, 0)} of churners. {n_hr:,} active customers match, with ${rev:,.0f} monthly revenue "
                    f"at risk. Contact them first, highest bill first.")
    net = df[df.internet_service != "No"]
    w, wo = net[net.tech_support == "Yes"], net[net.tech_support == "No"]
    if len(w) >= 100 and len(wo) >= 100 and wo.churn_flag.mean() - w.churn_flag.mean() > 0.05:
        recs.append(f"Support: internet customers without Tech Support churn at {pct(wo.churn_flag.mean())} (n={len(wo):,}) vs "
                    f"{pct(w.churn_flag.mean())} with it (n={len(w):,}). Test a Tech Support trial for at-risk customers; "
                    f"this is an association, not proof that the service reduces churn.")
    return recs


def dashboard_3(df, out):
    overall = df.churn_flag.mean()
    fig = plt.figure(figsize=FIGSIZE, dpi=DPI)
    frame(fig, "Retention & Risk", 3)
    n_hr = int(df.high_risk_flag.sum())
    prof = df[df.risk_profile_match == 1]
    precision = prof.churn_flag.mean() if len(prof) else float("nan")
    capture = prof.churn_flag.sum() / df.churn_flag.sum() if df.churn_flag.sum() else float("nan")
    rev_risk = df.loc[df.high_risk_flag == 1, "monthly_charges"].sum()

    # rule quality card
    ax = fig.add_axes([0.04, 0.60, 0.20, 0.26])
    ax.set_axis_off()
    ax.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0,rounding_size=0.04", fc=LIGHT, ec="#D9D9D9",
                                transform=ax.transAxes))
    ax.text(0.06, 0.92, "How good is the risk rule?", fontsize=11.5, fontweight="bold", color=NAVY, va="top")
    ax.text(0.06, 0.81, "Month-to-month, tenure <= 12 mo,\nhas internet, no Tech Support", fontsize=8, color=GREY, va="top")
    lines = [("Churn rate of matches", pct(precision), RED), ("Overall churn rate", pct(overall), NAVY),
             ("Lift vs overall", f"{precision / overall:.2f}x", RED), ("Share of churners captured", pct(capture), BLUE),
             ("Active high-risk customers", f"{n_hr:,}", RED), ("Monthly revenue at risk", f"${rev_risk:,.0f}", RED)]
    for i, (lab, val, col) in enumerate(lines):
        y = 0.60 - i * 0.095
        ax.text(0.06, y, lab, fontsize=8.8, color=DARK, va="center")
        ax.text(0.94, y, val, fontsize=11, fontweight="bold", color=col, va="center", ha="right")

    # top risk segments
    g = (df.groupby(["contract_category", "tenure_group", "internet_service"])
           .agg(n=("churn_flag", "size"), churned=("churn_flag", "sum"), rate=("churn_flag", "mean")).reset_index())
    g = g[g.n >= 50].sort_values("rate", ascending=False).head(10)
    g["lab"] = g.contract_category.str.replace("Month-to-month", "M2M") + " | " + g.tenure_group + " | " + g.internet_service
    t = g.set_index("lab")[["n", "rate", "churned"]]
    hbar(fig.add_axes([0.42, 0.60, 0.20, 0.25]), t, overall, "Top 10 risk segments (50+ customers)",
         "M2M = Month-to-month. Rate and volume together")

    # revenue by risk tier
    order = ["Churned", "High risk", "Watch", "Stable"]
    cols = {"Churned": RED, "High risk": AMBER, "Watch": LBLUE, "Stable": BLUE}
    rv = df.groupby("risk_segment").monthly_charges.sum().reindex(order).fillna(0)
    ax = fig.add_axes([0.74, 0.60, 0.22, 0.25])
    ax.barh(range(4), rv.values, color=[cols[o] for o in order], height=0.62)
    ax.set_yticks(range(4))
    ax.set_yticklabels(order, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlim(0, rv.max() * 1.45)
    for i, v in enumerate(rv.values):
        ax.text(v + rv.max() * 0.015, i, f"${v:,.0f}", va="center", fontsize=8.5, color=DARK)
    ax.set_xticks([])
    clean_ax(ax)
    title_ax(ax, "Monthly billing by risk tier", "High risk = revenue at risk. Churned = already lost")

    # risk distribution
    dist = df.pivot_table(index="contract_category", columns="risk_segment", values="customer_id", aggfunc="count").reindex(columns=order).fillna(0)
    ax = fig.add_axes([0.125, 0.285, 0.20, 0.20])
    left = np.zeros(len(dist))
    for o in order:
        ax.barh(range(len(dist)), dist[o].values, left=left, color=cols[o], height=0.55, label=o)
        for i, (l, v) in enumerate(zip(left, dist[o].values)):
            if v > dist.values.sum() * 0.045:
                ax.text(l + v / 2, i, f"{int(v):,}", ha="center", va="center", fontsize=8, color="white" if o in ("Churned", "Stable") else DARK)
        left += dist[o].values
    ax.set_yticks(range(len(dist)))
    ax.set_yticklabels(dist.index, fontsize=9)
    ax.invert_yaxis()
    ax.set_xticks([])
    ax.legend(ncol=4, fontsize=7.5, frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.04), handlelength=1)
    clean_ax(ax)
    title_ax(ax, "Customers by risk tier", "Rule flags only month-to-month, so long-term plans are Churned or Stable")

    # churn reasons
    rs = df[df.churn_flag == 1].churn_reason.value_counts().head(10)
    ax = fig.add_axes([0.46, 0.285, 0.16, 0.20])
    if len(rs):
        ax.barh(range(len(rs)), rs.values, color=RED, height=0.62)
        ax.set_yticks(range(len(rs)))
        ax.set_yticklabels([textwrap.shorten(str(i), 34, placeholder="...") for i in rs.index], fontsize=7.8)
        ax.invert_yaxis()
        ax.set_xlim(0, rs.max() * 1.3)
        for i, v in enumerate(rs.values):
            ax.text(v + rs.max() * 0.015, i, f"{v:,}", va="center", fontsize=8, color=DARK)
    ax.set_xticks([])
    clean_ax(ax)
    title_ax(ax, "Top stated churn reasons", "Churned customers only; self-reported")

    # drivers
    dr = driver_table(df, overall)
    ax = fig.add_axes([0.745, 0.285, 0.18, 0.20])
    ax.barh(range(len(dr)), dr.gap * 100, color=[RED if v > 0 else BLUE for v in dr.gap], height=0.62)
    ax.set_yticks(range(len(dr)))
    ax.set_yticklabels(dr.label, fontsize=7.6)
    ax.invert_yaxis()
    ax.axvline(0, color=DARK, lw=0.8)
    span = max(dr.gap.abs().max() * 100, 1)
    ax.set_xlim(-span * 1.1, span * 2.6)
    for i, (v, n) in enumerate(zip(dr.gap, dr.n)):
        ax.text(max(v, 0) * 100 + span * 0.06, i, f"{v * 100:+.1f} pts (n={n:,})",
                va="center", ha="left", fontsize=7.4, color=DARK)
    ax.set_xticks([])
    clean_ax(ax)
    title_ax(ax, "Attribute values vs average churn",
             f"Percentage-point gap vs overall {pct(overall)}; 100+ customers. Association, not cause")

    # recommendations
    recs = recommendations(df, overall)
    ax = fig.add_axes([0.04, 0.045, 0.92, 0.17])
    ax.set_axis_off()
    ax.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0,rounding_size=0.03", fc="#FBF3F2", ec="#E6C3BF",
                                transform=ax.transAxes))
    ax.text(0.015, 0.90, "Recommended retention actions (generated from this data; hypotheses to A/B test)",
            fontsize=10.5, fontweight="bold", color=RED, va="top")
    y = 0.72
    if not recs:
        ax.text(0.015, y, "No recommendation met its evidence threshold in this data.", fontsize=8.8, color=DARK, va="top")
    for r_ in recs:
        wrapped = textwrap.fill(r_, 205)
        ax.text(0.015, y, "-  " + wrapped.replace("\n", "\n    "), fontsize=8.3, color=DARK, va="top", linespacing=1.25)
        y -= 0.115 * (wrapped.count("\n") + 1) + 0.045
    fig.savefig(out, dpi=DPI)
    plt.close(fig)


def build(features_csv=None, out_dir=None):
    features_csv = Path(features_csv) if features_csv else ROOT / "data" / "cleaned" / "churn_features.csv"
    out_dir = Path(out_dir) if out_dir else ROOT / "screenshots"
    if not features_csv.exists():
        sys.exit(f"{features_csv} not found. Run `python run_all.py` first.")
    out_dir.mkdir(parents=True, exist_ok=True)
    df = prepare(pd.read_csv(features_csv))
    paths = []
    for fn, name in [(dashboard_1, "dashboard_1_executive.png"), (dashboard_2, "dashboard_2_segmentation.png"),
                     (dashboard_3, "dashboard_3_risk.png")]:
        p = out_dir / name
        fn(df, p)
        paths.append(p)
        print("  wrote", p)
    return paths


if __name__ == "__main__":
    build()
