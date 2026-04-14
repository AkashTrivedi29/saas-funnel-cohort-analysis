# SaaS Product Funnel & Cohort Retention Analysis

🔗 **Live Dashboard:** [View on Tableau Public](https://public.tableau.com/app/profile/akash.trivedi4762/viz/SaaSFunnelandCohortRetentionAnalysis/SaaSProductAnalyticsFunnelCohortRetentionPlanAnalysis)

> **Tools:** Python · Pandas · Matplotlib · Seaborn · Tableau Public
> **Data:** Synthetic SaaS event log — 3,000 users · 63,658 events · 18 monthly cohorts
> **Author:** Akash Trivedi · [LinkedIn](https://linkedin.com/in/akash-trivedi) · [Tableau Public](https://public.tableau.com/app/profile/akash.trivedi4762)

---

## Business Question

**Which user behaviours in the first 30 days predict long-term retention?**

This project analyses a B2B SaaS product's full user journey — from signup through activation, feature adoption, and conversion — to identify the key behavioural signals that distinguish retained users from churned ones.

---

## Key Findings

| Metric | Value |
|--------|-------|
| Total Users Analysed | **3,000** |
| Signup → Activation Rate | **71.8%** (First Project Created) |
| Signup → Paid Conversion | **7.9%** |
| Biggest Funnel Drop-off | **Invited Team Member (−36.2pp)** |
| #1 Retention Predictor | **Report Generated (+13.1pp Day-30 retention)** |
| Best Acquisition Channel | **Referral (74.7% Day-30 retention)** |
| Average Day-30 Retention | **58.0%** |
| Enterprise vs Free Retention Gap | **~3× at Day 30** |

---

## Conversion Funnel

| Step | Users | % of Total | Drop-off |
|------|-------|------------|---------|
| Signup | 3,000 | 100% | — |
| Email Verified | 2,581 | 86.0% | −14% |
| Profile Completed | 2,343 | 78.1% | −9.2% |
| First Project Created | 2,155 | 71.8% | −8% |
| First Task Created | 1,983 | 66.1% | −8% |
| Invited Team Member | 1,265 | 42.2% | **−36.2%** ← biggest drop |
| Integration Connected | 922 | 30.7% | −27.1% |
| Converted to Paid | 238 | 7.9% | −74.2% |

---

## Cohort Retention Summary

| Plan | Day 7 | Day 14 | Day 30 | Day 60 | Day 90 |
|------|-------|--------|--------|--------|--------|
| Free | ~65% | ~52% | ~28% | ~12% | ~4% |
| Pro | ~82% | ~70% | ~55% | ~28% | ~10% |
| Enterprise | ~94% | ~88% | ~80% | ~52% | ~25% |

---

## Visualizations

| # | Chart | Insight |
|---|-------|---------|
| 1 | Conversion Funnel | Team invite is the critical drop-off point (-36pp) |
| 2 | Cohort Retention Heatmap | Recent cohorts incomplete; older cohorts show ~60% Day-30 |
| 3 | Retention Curves by Plan | Enterprise retains 3× better than Free at Day 30 |
| 4 | Feature → Retention Impact | Report generation = strongest predictor (+13.1pp) |
| 5 | Channel Performance | Referral > Organic > Paid for long-term retention |
| 6 | Monthly Signups + MRR | Steady growth trend through 2023–2024 |
| 7 | Retention by Company Size | 200+ employee companies retain 2× vs solo users |
| 8 | Time-to-Key-Action | Median time to first team invite = 8 days |

---

## Project Structure

```
saas-funnel-cohort-analysis/
├── data/
│   ├── users.csv                # 3,000 users with plan, channel, cohort
│   ├── events.csv               # 63,658 timestamped user events
│   ├── funnel_analysis.csv      # Step-by-step funnel counts
│   ├── cohort_retention.csv     # 18×6 cohort retention matrix
│   ├── retention_by_plan.csv    # Retention curves per plan
│   ├── behaviour_impact.csv     # Feature → retention impact table
│   ├── channel_performance.csv  # Acquisition channel KPIs
│   └── monthly_growth.csv       # Monthly signups + MRR
├── notebooks/
│   ├── 01_data_generation.py    # Synthetic SaaS event log
│   └── 02_funnel_cohort_analysis.py  # Full analysis + 8 charts
├── charts/
│   ├── 01_conversion_funnel.png
│   ├── 02_cohort_heatmap.png
│   ├── 03_retention_by_plan.png
│   ├── 04_behaviour_retention.png
│   ├── 05_channel_performance.png
│   ├── 06_monthly_growth.png
│   ├── 07_retention_by_company_size.png
│   └── 08_time_to_action.png
└── README.md
```

---

## How to Run

```bash
git clone https://github.com/AkashTrivedi29/saas-funnel-cohort-analysis
cd saas-funnel-cohort-analysis
pip install pandas numpy matplotlib seaborn

python notebooks/01_data_generation.py
python notebooks/02_funnel_cohort_analysis.py
```

---

## Business Recommendations

**Immediate Actions:**
- **Fix the team invite drop-off** — 57.8% of users never invite a teammate. Add an in-app prompt on Day 3 nudging users to invite colleagues. This single step predicts significantly higher retention.
- **Push Report Generation** — users who generate a report retain at +13.1pp higher Day-30 rate. Add an automated "Your first report is ready" email at Day 5.

**Growth Actions:**
- **Double down on Referral channel** — 74.7% Day-30 retention vs 55% for Paid Search. Invest in referral program incentives.
- **Target 11-50 employee companies** — 2× retention vs solo users with similar CAC. Re-focus paid ads to SMB segment.

**Monetisation:**
- **Free → Pro conversion at 7.9%** — benchmark is 5–10% for B2B SaaS, so this is healthy. Focus on converting "Potential Loyal" users (activated but not converted) with targeted upgrade nudges at Day 14.

---

## Technologies Used

| Tool | Purpose |
|------|---------|
| Python 3.10 | Event simulation, funnel + cohort calculation |
| Pandas | Data wrangling, pivot tables, time-series aggregation |
| Matplotlib / Seaborn | 8 analytical charts including heatmap |
| Power BI / Tableau | Interactive dashboard |
| GitHub | Version control + portfolio |

