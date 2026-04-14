"""
=============================================================================
PROJECT 3: SaaS Product Funnel & Cohort Analysis
Data Generator — Synthetic SaaS Event Log
=============================================================================
Business Question:
  Which user behaviours in the first 30 days predict long-term retention?

Simulates a B2B SaaS product (project management / productivity tool) with:
  - 3,000 users signing up Jan 2023 – Jun 2024 (18 cohorts)
  - 12 event types across the user journey
  - Realistic churn curve (50% churn by day 30, 70% by day 90)
  - Feature adoption patterns linked to retention
  - Subscription tiers: Free, Pro, Enterprise

Key behaviours tracked:
  - Funnel: Signup → Activation → Feature Use → Collaboration → Conversion
  - Cohort: Monthly retention rates (Day 7, 14, 30, 60, 90)
  - Predictors: Invites sent, integrations connected, core feature usage
=============================================================================
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random

np.random.seed(42)
random.seed(42)

# ---------------------------------------------------------------------------
# 1. User Base
# ---------------------------------------------------------------------------
n_users = 3000
start_date = datetime(2023, 1, 1)
end_date   = datetime(2024, 6, 30)
date_range = (end_date - start_date).days

# Acquisition channels
channels = {
    "Organic Search":  0.35,
    "Paid Search":     0.22,
    "Product Hunt":    0.08,
    "Referral":        0.15,
    "Direct":          0.12,
    "Social Media":    0.08,
}

# Plans
plans = {
    "Free":       0.65,
    "Pro":        0.28,
    "Enterprise": 0.07,
}

# Company sizes
company_sizes = {
    "Solo":        0.30,
    "2-10":        0.35,
    "11-50":       0.20,
    "51-200":      0.10,
    "200+":        0.05,
}

# Retention probability by plan (30-day)
plan_retention = {
    "Free":       0.28,
    "Pro":        0.55,
    "Enterprise": 0.80,
}

# Retention boost by channel
channel_retention_boost = {
    "Organic Search": 0.05,
    "Paid Search":    -0.05,
    "Product Hunt":   0.10,
    "Referral":       0.15,
    "Direct":         0.05,
    "Social Media":   -0.03,
}

users = []
for uid in range(1, n_users + 1):
    signup_date = start_date + timedelta(days=np.random.randint(0, date_range))
    plan    = np.random.choice(list(plans.keys()), p=list(plans.values()))
    channel = np.random.choice(list(channels.keys()), p=list(channels.values()))
    size    = np.random.choice(list(company_sizes.keys()), p=list(company_sizes.values()))

    # Base retention probability
    base_ret = plan_retention[plan] + channel_retention_boost[channel]
    # Company size boost
    if size in ["11-50", "51-200", "200+"]:
        base_ret += 0.08
    base_ret = max(0.10, min(0.90, base_ret))

    users.append({
        "user_id":        f"USR{uid:05d}",
        "signup_date":    signup_date,
        "plan":           plan,
        "channel":        channel,
        "company_size":   size,
        "cohort_month":   signup_date.strftime("%Y-%m"),
        "retention_prob": base_ret,
    })

df_users = pd.DataFrame(users)

# ---------------------------------------------------------------------------
# 2. Event Generation
# ---------------------------------------------------------------------------
# Funnel events in order
funnel_events = [
    "signup",
    "email_verified",
    "profile_completed",
    "first_project_created",
    "first_task_created",
    "invited_team_member",
    "integration_connected",
    "dashboard_viewed",
    "report_generated",
    "upgrade_page_viewed",
    "plan_upgraded",
    "churned",
]

# Probability of reaching each funnel step (cumulative drop-off)
funnel_probs = {
    "signup":               1.00,
    "email_verified":       0.82,
    "profile_completed":    0.71,
    "first_project_created":0.65,
    "first_task_created":   0.60,
    "invited_team_member":  0.38,
    "integration_connected":0.29,
    "dashboard_viewed":     0.55,
    "report_generated":     0.32,
    "upgrade_page_viewed":  0.24,
    "plan_upgraded":        0.08,
}

# Time offsets from signup (days)
event_timing = {
    "signup":               (0, 0),
    "email_verified":       (0, 1),
    "profile_completed":    (0, 2),
    "first_project_created":(0, 3),
    "first_task_created":   (0, 4),
    "invited_team_member":  (1, 14),
    "integration_connected":(2, 21),
    "dashboard_viewed":     (1, 7),
    "report_generated":     (7, 30),
    "upgrade_page_viewed":  (5, 45),
    "plan_upgraded":        (14, 60),
}

events = []
for _, user in df_users.iterrows():
    # Always record signup
    events.append({
        "user_id":    user["user_id"],
        "event":      "signup",
        "event_date": user["signup_date"],
        "days_since_signup": 0,
    })

    # Check each funnel step
    for evt, prob in funnel_probs.items():
        if evt == "signup":
            continue
        # Adjust prob by plan
        adj_prob = prob
        if user["plan"] == "Pro":       adj_prob = min(prob * 1.3, 0.95)
        if user["plan"] == "Enterprise":adj_prob = min(prob * 1.6, 0.98)

        if np.random.random() < adj_prob:
            timing = event_timing[evt]
            days_offset = np.random.randint(timing[0], max(timing[1], timing[0]+1))
            event_date = user["signup_date"] + timedelta(days=days_offset)
            if event_date <= end_date:
                events.append({
                    "user_id":    user["user_id"],
                    "event":      evt,
                    "event_date": event_date,
                    "days_since_signup": days_offset,
                })

    # Daily active usage events (for retained users)
    ret_prob = user["retention_prob"]
    for day in range(1, 91):
        # Churn curve: exponential decay
        daily_active_prob = ret_prob * np.exp(-day * 0.025)
        if np.random.random() < daily_active_prob:
            event_date = user["signup_date"] + timedelta(days=day)
            if event_date <= end_date:
                evt_type = np.random.choice([
                    "session_started", "task_created", "project_updated",
                    "comment_added", "file_uploaded", "search_performed"
                ])
                events.append({
                    "user_id":    user["user_id"],
                    "event":      evt_type,
                    "event_date": event_date,
                    "days_since_signup": day,
                })

df_events = pd.DataFrame(events)
df_events["event_date"] = pd.to_datetime(df_events["event_date"])

print(f"✅ Users generated: {len(df_users):,}")
print(f"✅ Events generated: {len(df_events):,}")
print(f"   Unique event types: {df_events['event'].nunique()}")
print(f"   Date range: {df_events['event_date'].min().date()} → {df_events['event_date'].max().date()}")
print(f"   Cohorts: {df_users['cohort_month'].nunique()} months")

df_users.to_csv("/sessions/dazzling-sweet-pascal/day3_saas/data/users.csv", index=False)
df_events.to_csv("/sessions/dazzling-sweet-pascal/day3_saas/data/events.csv", index=False)
print("\n✅ Data saved")
