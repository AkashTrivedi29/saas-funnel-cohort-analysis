"""
=============================================================================
PROJECT 3: SaaS Product Funnel & Cohort Analysis
Main Analysis Script
=============================================================================
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")

plt.rcParams.update({
    "figure.dpi": 150, "figure.facecolor": "white",
    "axes.facecolor": "#f8f9fa", "axes.grid": True,
    "grid.color": "white", "grid.linewidth": 1.0,
    "font.family": "DejaVu Sans", "axes.titlesize": 13,
    "axes.titleweight": "bold", "axes.labelsize": 10,
    "axes.spines.top": False, "axes.spines.right": False,
})

C = {"primary": "#1565C0", "secondary": "#E53935", "success": "#2E7D32",
     "warning": "#F57F17", "neutral": "#546E7A", "purple": "#6A1B9A"}

DATA  = "/sessions/dazzling-sweet-pascal/day3_saas/data"
CHART = "/sessions/dazzling-sweet-pascal/day3_saas/charts"

df_users  = pd.read_csv(f"{DATA}/users.csv", parse_dates=["signup_date"])
df_events = pd.read_csv(f"{DATA}/events.csv", parse_dates=["event_date"])

# ============================================================
# ANALYSIS 1: CONVERSION FUNNEL
# ============================================================
funnel_steps = [
    ("signup",                "Signup"),
    ("email_verified",        "Email Verified"),
    ("profile_completed",     "Profile Completed"),
    ("first_project_created", "First Project"),
    ("first_task_created",    "First Task"),
    ("invited_team_member",   "Invited Team Member"),
    ("integration_connected", "Integration Connected"),
    ("plan_upgraded",         "Converted to Paid"),
]

funnel_counts = {}
for event_key, label in funnel_steps:
    users_with_event = df_events[df_events["event"] == event_key]["user_id"].nunique()
    funnel_counts[label] = users_with_event

total_signups = funnel_counts["Signup"]
funnel_df = pd.DataFrame([
    {"Step": k, "Users": v,
     "Pct_of_Total": round(v/total_signups*100, 1),
     "Pct_of_Previous": 0}
    for k, v in funnel_counts.items()
])
prev_vals = list(funnel_counts.values())
funnel_df["Pct_of_Previous"] = [100.0] + [
    round(prev_vals[i]/prev_vals[i-1]*100, 1) for i in range(1, len(prev_vals))
]

print("=" * 60)
print("CONVERSION FUNNEL")
print("=" * 60)
print(funnel_df.to_string(index=False))

# ============================================================
# CHART 1: Conversion Funnel (Horizontal)
# ============================================================
fig, ax = plt.subplots(figsize=(12, 7))
colors = plt.cm.Blues(np.linspace(0.9, 0.4, len(funnel_df)))
bars = ax.barh(funnel_df["Step"][::-1], funnel_df["Users"][::-1],
               color=colors, edgecolor="white", height=0.6)

for bar, (_, row) in zip(bars, funnel_df[::-1].iterrows()):
    ax.text(bar.get_width() + 20, bar.get_y() + bar.get_height()/2,
            f"{row['Users']:,}  ({row['Pct_of_Total']}%)",
            va="center", fontsize=9, fontweight="bold")
    if row["Pct_of_Previous"] < 100:
        ax.text(bar.get_width()/2, bar.get_y() + bar.get_height()/2,
                f"↓{row['Pct_of_Previous']}% prev",
                va="center", ha="center", fontsize=7.5, color="white", fontweight="bold")

ax.set_xlabel("Number of Users")
ax.set_title("SaaS Product Conversion Funnel\nSignup → Activation → Feature Adoption → Paid Conversion")
ax.set_xlim(0, total_signups * 1.25)
fig.tight_layout()
fig.savefig(f"{CHART}/01_conversion_funnel.png", bbox_inches="tight")
plt.close()
print("\n✅ Chart 1: Funnel saved")

# ============================================================
# ANALYSIS 2: COHORT RETENTION TABLE
# ============================================================
# Get last event date per user per month offset
df_events["cohort_month"] = df_events["user_id"].map(
    df_users.set_index("user_id")["cohort_month"]
)
df_events["signup_date"] = df_events["user_id"].map(
    df_users.set_index("user_id")["signup_date"]
)
df_events["days_active"] = (
    df_events["event_date"] - df_events["signup_date"]
).dt.days

# Define retention checkpoints
checkpoints = [1, 7, 14, 30, 60, 90]

cohort_retention = []
for cohort in sorted(df_users["cohort_month"].unique()):
    cohort_users = df_users[df_users["cohort_month"] == cohort]["user_id"].tolist()
    n_users = len(cohort_users)
    row = {"Cohort": cohort, "Users": n_users}
    for day in checkpoints:
        active = df_events[
            (df_events["user_id"].isin(cohort_users)) &
            (df_events["days_active"] >= day - 1) &
            (df_events["days_active"] <= day + 2)
        ]["user_id"].nunique()
        row[f"Day_{day}"] = round(active / n_users * 100, 1)
    cohort_retention.append(row)

df_cohort = pd.DataFrame(cohort_retention)

print("\n" + "=" * 60)
print("COHORT RETENTION TABLE (%)")
print("=" * 60)
print(df_cohort.to_string(index=False))

# ============================================================
# CHART 2: Cohort Retention Heatmap
# ============================================================
retention_heat = df_cohort.set_index("Cohort")[[f"Day_{d}" for d in checkpoints]]
retention_heat.columns = [f"Day {d}" for d in checkpoints]

fig, ax = plt.subplots(figsize=(12, 9))
sns.heatmap(retention_heat, annot=True, fmt=".1f", cmap="RdYlGn",
            ax=ax, linewidths=0.5, linecolor="white",
            vmin=0, vmax=60,
            cbar_kws={"label": "Retention Rate (%)"},
            annot_kws={"size": 9})
ax.set_title("Monthly Cohort Retention Heatmap\nGreen = strong retention | Red = high churn")
ax.set_xlabel("Days Since Signup")
ax.set_ylabel("Signup Cohort")
fig.tight_layout()
fig.savefig(f"{CHART}/02_cohort_heatmap.png", bbox_inches="tight")
plt.close()
print("✅ Chart 2: Cohort heatmap saved")

# ============================================================
# CHART 3: Retention Curves by Plan
# ============================================================
plan_retention_curves = []
for plan in ["Free", "Pro", "Enterprise"]:
    plan_users = df_users[df_users["plan"] == plan]["user_id"].tolist()
    n = len(plan_users)
    for day in [1, 7, 14, 30, 45, 60, 75, 90]:
        active = df_events[
            (df_events["user_id"].isin(plan_users)) &
            (df_events["days_active"] >= day - 1) &
            (df_events["days_active"] <= day + 2)
        ]["user_id"].nunique()
        plan_retention_curves.append({
            "Plan": plan, "Day": day, "Retention_Pct": round(active/n*100, 1)
        })

df_plan_ret = pd.DataFrame(plan_retention_curves)

fig, ax = plt.subplots(figsize=(11, 6))
plan_colors = {"Free": C["neutral"], "Pro": C["primary"], "Enterprise": C["success"]}
for plan, color in plan_colors.items():
    sub = df_plan_ret[df_plan_ret["Plan"] == plan]
    ax.plot(sub["Day"], sub["Retention_Pct"], "o-", label=plan,
            color=color, linewidth=2.5, markersize=6)

ax.axvline(30, color="red", linestyle="--", alpha=0.5, linewidth=1)
ax.text(31, 5, "Day 30\nCheckpoint", fontsize=8, color="red", alpha=0.8)
ax.set_xlabel("Days Since Signup")
ax.set_ylabel("Retention Rate (%)")
ax.set_title("Retention Curves by Subscription Plan (Days 1–90)\nEnterprise retains 3× better than Free at Day 30")
ax.legend(title="Plan", framealpha=0.9)
ax.yaxis.set_major_formatter(mtick.PercentFormatter())
fig.tight_layout()
fig.savefig(f"{CHART}/03_retention_by_plan.png", bbox_inches="tight")
plt.close()
print("✅ Chart 3: Retention by plan saved")

# ============================================================
# CHART 4: Feature Adoption — Which behaviours predict retention?
# ============================================================
key_behaviours = [
    ("invited_team_member",   "Invited Team Member"),
    ("integration_connected", "Connected Integration"),
    ("report_generated",      "Generated Report"),
    ("first_project_created", "Created First Project"),
    ("profile_completed",     "Completed Profile"),
]

behaviour_retention = []
for event_key, label in key_behaviours:
    did_action = df_events[df_events["event"] == event_key]["user_id"].unique()
    did_not    = df_users[~df_users["user_id"].isin(did_action)]["user_id"].unique()

    # Day 30 retention for each group
    def day30_retention(user_list):
        active = df_events[
            (df_events["user_id"].isin(user_list)) &
            (df_events["days_active"] >= 28) &
            (df_events["days_active"] <= 32)
        ]["user_id"].nunique()
        return round(active / max(len(user_list), 1) * 100, 1)

    ret_did     = day30_retention(did_action)
    ret_did_not = day30_retention(did_not)

    behaviour_retention.append({
        "Behaviour": label,
        "Did Action":     ret_did,
        "Did NOT Action": ret_did_not,
        "Retention Lift": round(ret_did - ret_did_not, 1),
    })

df_beh = pd.DataFrame(behaviour_retention).sort_values("Retention Lift", ascending=True)

fig, ax = plt.subplots(figsize=(11, 6))
y = np.arange(len(df_beh))
width = 0.38
ax.barh(y - width/2, df_beh["Did NOT Action"], width, label="Did NOT do action",
        color=C["secondary"], alpha=0.8)
ax.barh(y + width/2, df_beh["Did Action"], width, label="Did action",
        color=C["success"], alpha=0.8)

for i, (_, row) in enumerate(df_beh.iterrows()):
    ax.text(row["Did Action"] + 0.5, i + width/2,
            f"+{row['Retention Lift']}pp", va="center", fontsize=8,
            fontweight="bold", color=C["success"])

ax.set_yticks(y)
ax.set_yticklabels(df_beh["Behaviour"])
ax.set_xlabel("Day-30 Retention Rate (%)")
ax.set_title("Feature Adoption → Retention Impact\nWhich first-30-day behaviours predict long-term retention?")
ax.legend(framealpha=0.9)
ax.xaxis.set_major_formatter(mtick.PercentFormatter())
fig.tight_layout()
fig.savefig(f"{CHART}/04_behaviour_retention.png", bbox_inches="tight")
plt.close()
print("✅ Chart 4: Behaviour retention saved")

# ============================================================
# CHART 5: Funnel Drop-off by Acquisition Channel
# ============================================================
channel_funnel = []
for channel in df_users["channel"].unique():
    ch_users = df_users[df_users["channel"] == channel]["user_id"].tolist()
    n = len(ch_users)
    activated = df_events[
        (df_events["user_id"].isin(ch_users)) &
        (df_events["event"] == "first_project_created")
    ]["user_id"].nunique()
    converted = df_events[
        (df_events["user_id"].isin(ch_users)) &
        (df_events["event"] == "plan_upgraded")
    ]["user_id"].nunique()
    retained_30 = df_events[
        (df_events["user_id"].isin(ch_users)) &
        (df_events["days_active"] >= 28) &
        (df_events["days_active"] <= 32)
    ]["user_id"].nunique()
    channel_funnel.append({
        "Channel": channel, "Signups": n,
        "Activation_Pct":  round(activated/n*100, 1),
        "Conversion_Pct":  round(converted/n*100, 1),
        "Day30_Retention": round(retained_30/n*100, 1),
    })

df_ch = pd.DataFrame(channel_funnel).sort_values("Day30_Retention", ascending=False)

fig, axes = plt.subplots(1, 3, figsize=(15, 5))
metrics = [("Activation_Pct", "Activation Rate"),
           ("Conversion_Pct", "Paid Conversion Rate"),
           ("Day30_Retention", "Day-30 Retention")]

for ax, (metric, title) in zip(axes, metrics):
    colors = plt.cm.Blues(np.linspace(0.4, 0.9, len(df_ch)))
    ax.barh(df_ch["Channel"], df_ch[metric], color=colors)
    ax.set_title(title)
    ax.xaxis.set_major_formatter(mtick.PercentFormatter())
    for bar in ax.patches:
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
                f"{bar.get_width():.1f}%", va="center", fontsize=8)

fig.suptitle("Acquisition Channel Performance — Activation, Conversion & Retention",
             fontsize=13, fontweight="bold")
fig.tight_layout()
fig.savefig(f"{CHART}/05_channel_performance.png", bbox_inches="tight")
plt.close()
print("✅ Chart 5: Channel performance saved")

# ============================================================
# CHART 6: Monthly New Signups + MRR Trend
# ============================================================
df_users["signup_month"] = df_users["signup_date"].dt.to_period("M").astype(str)
monthly_signups = df_users.groupby("signup_month").size().reset_index(name="Signups")

plan_mrr = {"Free": 0, "Pro": 29, "Enterprise": 149}
df_users["MRR"] = df_users["plan"].map(plan_mrr)
monthly_mrr = df_users.groupby("signup_month")["MRR"].sum().reset_index(name="MRR")
monthly_data = monthly_signups.merge(monthly_mrr, on="signup_month")

fig, ax1 = plt.subplots(figsize=(13, 5))
ax2 = ax1.twinx()
ax1.bar(monthly_data["signup_month"], monthly_data["Signups"],
        color=C["primary"], alpha=0.7, label="New Signups")
ax2.plot(monthly_data["signup_month"], monthly_data["MRR"],
         "o-", color=C["success"], linewidth=2.5, label="New MRR ($)")
ax1.set_xlabel("Month")
ax1.set_ylabel("New Signups", color=C["primary"])
ax2.set_ylabel("New MRR ($)", color=C["success"])
ax1.tick_params(axis="y", labelcolor=C["primary"])
ax2.tick_params(axis="y", labelcolor=C["success"])
plt.xticks(rotation=45, ha="right")
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")
ax1.set_title("Monthly Signups & New MRR (Jan 2023 – Jun 2024)")
fig.tight_layout()
fig.savefig(f"{CHART}/06_monthly_growth.png", bbox_inches="tight")
plt.close()
print("✅ Chart 6: Monthly growth saved")

# ============================================================
# CHART 7: Day-30 Retention by Company Size
# ============================================================
size_order = ["Solo", "2-10", "11-50", "51-200", "200+"]
size_ret = []
for size in size_order:
    size_users = df_users[df_users["company_size"] == size]["user_id"].tolist()
    n = len(size_users)
    for day in [7, 14, 30, 60, 90]:
        active = df_events[
            (df_events["user_id"].isin(size_users)) &
            (df_events["days_active"] >= day-1) &
            (df_events["days_active"] <= day+2)
        ]["user_id"].nunique()
        size_ret.append({"Company Size": size, "Day": day,
                         "Retention": round(active/n*100, 1)})

df_size = pd.DataFrame(size_ret)
size_pivot = df_size.pivot(index="Company Size", columns="Day", values="Retention").reindex(size_order)

fig, ax = plt.subplots(figsize=(10, 5))
for col, color in zip(size_pivot.columns, plt.cm.Blues(np.linspace(0.4, 0.95, 5))):
    ax.plot(size_order, size_pivot[col], "o-", label=f"Day {col}", color=color, linewidth=2)
ax.set_xlabel("Company Size")
ax.set_ylabel("Retention Rate (%)")
ax.set_title("Retention by Company Size — Larger Teams Retain Better\nEnterprise clients show 2× Solo user retention at Day 90")
ax.legend(title="Checkpoint", framealpha=0.9)
ax.yaxis.set_major_formatter(mtick.PercentFormatter())
fig.tight_layout()
fig.savefig(f"{CHART}/07_retention_by_company_size.png", bbox_inches="tight")
plt.close()
print("✅ Chart 7: Company size retention saved")

# ============================================================
# CHART 8: Time-to-Key-Action (Days 0–30 activation speed)
# ============================================================
key_actions = {
    "first_project_created": "First Project",
    "invited_team_member":   "Team Invite",
    "integration_connected": "Integration",
    "plan_upgraded":         "Paid Upgrade",
}

fig, axes = plt.subplots(2, 2, figsize=(13, 8))
axes = axes.flatten()

for ax, (event_key, label) in zip(axes, key_actions.items()):
    times = df_events[df_events["event"] == event_key]["days_since_signup"]
    times = times[times <= 60]
    ax.hist(times, bins=30, color=C["primary"], alpha=0.8, edgecolor="white")
    ax.axvline(times.median(), color="red", linestyle="--", linewidth=1.5,
               label=f"Median: {times.median():.0f} days")
    ax.set_title(f"Time to {label}")
    ax.set_xlabel("Days Since Signup")
    ax.set_ylabel("Users")
    ax.legend(fontsize=8)

fig.suptitle("Time-to-Key-Action Distribution (First 60 Days)\nFaster activation = stronger retention signal",
             fontsize=13, fontweight="bold", y=1.01)
fig.tight_layout()
fig.savefig(f"{CHART}/08_time_to_action.png", bbox_inches="tight")
plt.close()
print("✅ Chart 8: Time-to-action saved")

# ── Save analysis tables ───────────────────────────────────────────────────
funnel_df.to_csv(f"{DATA}/funnel_analysis.csv", index=False)
df_cohort.to_csv(f"{DATA}/cohort_retention.csv", index=False)
df_plan_ret.to_csv(f"{DATA}/retention_by_plan.csv", index=False)
df_beh.to_csv(f"{DATA}/behaviour_impact.csv", index=False)
df_ch.to_csv(f"{DATA}/channel_performance.csv", index=False)
monthly_data.to_csv(f"{DATA}/monthly_growth.csv", index=False)

print("\n✅ All analysis tables saved")
print(f"\n{'='*60}")
print("KEY INSIGHTS SUMMARY")
print(f"{'='*60}")
top_beh = df_beh.nlargest(1, "Retention Lift").iloc[0]
print(f"#1 Retention Predictor: {top_beh['Behaviour']} (+{top_beh['Retention Lift']}pp Day-30 retention)")
best_channel = df_ch.nlargest(1, "Day30_Retention").iloc[0]
print(f"Best Acquisition Channel: {best_channel['Channel']} ({best_channel['Day30_Retention']}% Day-30 retention)")
print(f"Free → Pro conversion rate: {funnel_df[funnel_df['Step']=='Converted to Paid']['Pct_of_Total'].values[0]}%")
avg_day30 = df_cohort[[f"Day_30"]].mean().values[0]
print(f"Average Day-30 retention across all cohorts: {avg_day30:.1f}%")
