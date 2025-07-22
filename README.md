# Influencer Campaign Performance Dashboard

Analyze and optimize influencer marketing campaigns with an interactive, data-driven dashboard built in Streamlit.

## Overview
This dashboard enables marketing teams to evaluate influencer performance, campaign ROI, and engagement across platforms. It features advanced filtering, actionable insights, and exportable analytics.

## Features
- **Comprehensive Filters:** Product, Platform, Influencer Type, Gender, Category, Campaign
- **Key Metrics:** Revenue, Spend, Orders, Campaigns, Top Influencer
- **Dynamic Insights:** Automated summary of top performers, engagement leaders, and ROI risks
- **Visual Analytics:**
  - ROAS and Incremental ROAS (bar charts)
  - Engagement vs Revenue (scatter)
  - Payout by Platform (pie)
  - Revenue Trend (line)
- **Performance Table:** Detailed influencer stats, ROAS, Incremental ROAS, and performance flags
- **Data Export:** Download filtered tables as CSV

## Incremental ROAS
Incremental ROAS estimates the true impact of influencer campaigns:

```
incremental_roas = (revenue - baseline_revenue) / spend
baseline_revenue = 200 × unique_users
```

Both ROAS and Incremental ROAS are available in the dashboard and visualized for comparison.

## Quick Start
1. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
2. Generate mock data:
   ```sh
   python generate_mock_data.py
   ```
3. Launch the dashboard:
   ```sh
   streamlit run dashboard_app.py
   ```

## Data Generation
Mock datasets are created using `generate_mock_data.py`:
- `influencers.csv`, `posts.csv`, `tracking_data.csv`, `payouts.csv`

## Assumptions
- Baseline revenue per user: ₹200
- Influencer types: Macro (≥100k), Micro (50k–99k), Nano (<50k)
- Engagement: (likes + comments) / reach
- ROAS: Revenue / Spend
- Incremental ROAS: Adjusted for baseline revenue

## Insights & Reporting
See `insights/insights_summary.pdf` for a full analysis of campaign results, top performers, and recommendations.

---