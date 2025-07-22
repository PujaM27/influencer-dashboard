import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Initialize engagement_df as empty DataFrame to avoid NameError
engagement_df = pd.DataFrame()

# Load data
@st.cache_data
def load_data():
    influencers = pd.read_csv('influencers.csv')
    posts = pd.read_csv('posts.csv')
    tracking = pd.read_csv('tracking_data.csv')
    payouts = pd.read_csv('payouts.csv')
    return influencers, posts, tracking, payouts

influencers, posts, tracking, payouts = load_data()

st.title('Influencer Campaign Performance Dashboard')

# --- SIDEBAR FILTERS ---
st.sidebar.header('Filters')

# Campaign filter
campaigns = tracking['campaign'].unique().tolist()
selected_campaign = st.sidebar.selectbox('Select Campaign', ['All'] + campaigns)

# Product filter
products = tracking['product'].unique().tolist()
product_filter = st.sidebar.multiselect('Product', products, default=products)

# Platform filter
platforms = influencers['platform'].unique().tolist()
platform_filter = st.sidebar.multiselect('Platform', platforms, default=platforms)

# Influencer Type (macro/micro/nano)
def get_influencer_type(followers):
    if followers >= 100000:
        return 'macro'
    elif followers >= 50000:
        return 'micro'
    else:
        return 'nano'
influencers['type'] = influencers['follower_count'].apply(get_influencer_type)
type_options = influencers['type'].unique().tolist()
type_filter = st.sidebar.multiselect('Influencer Type', type_options, default=type_options)

# Gender filter
genders = influencers['gender'].unique().tolist()
gender_filter = st.sidebar.multiselect('Gender', genders, default=genders)

# Category filter
categories = influencers['category'].unique().tolist()
category_filter = st.sidebar.multiselect('Category', categories, default=categories)

# --- FILTER DATA ---
filtered_tracking = tracking[
    tracking['product'].isin(product_filter) &
    tracking['source'].isin(platform_filter)
]
if selected_campaign != 'All':
    filtered_tracking = filtered_tracking[filtered_tracking['campaign'] == selected_campaign]

filtered_influencers = influencers[
    influencers['platform'].isin(platform_filter) &
    influencers['type'].isin(type_filter) &
    influencers['gender'].isin(gender_filter) &
    influencers['category'].isin(category_filter)
]
filtered_influencers = filtered_influencers[filtered_influencers['ID'].isin(filtered_tracking['influencer_id'].unique())]
filtered_payouts = payouts[payouts['influencer_id'].isin(filtered_influencers['ID'])]

# --- Prepare influencer performance data (perf_df, perf_display) ---
perf_df = filtered_influencers[['ID', 'name', 'category', 'platform', 'follower_count', 'type']].copy()

# Aggregate post metrics
post_agg = posts[posts['influencer_id'].isin(perf_df['ID'])].groupby('influencer_id').agg({
    'reach': 'sum',
    'likes': 'sum',
    'comments': 'sum'
}).reset_index().rename(columns={'influencer_id': 'ID'})
perf_df = perf_df.merge(post_agg, on='ID', how='left')

# Aggregate tracking metrics
track_agg = filtered_tracking.groupby('influencer_id').agg({
    'orders': 'sum',
    'revenue': 'sum'
}).reset_index().rename(columns={'influencer_id': 'ID'})
perf_df = perf_df.merge(track_agg, on='ID', how='left')

# Payouts
payout_agg = filtered_payouts[['influencer_id', 'total_payout']].rename(columns={'influencer_id': 'ID'})
perf_df = perf_df.merge(payout_agg, on='ID', how='left')

# ROAS
perf_df['ROAS'] = perf_df['revenue'] / perf_df['total_payout']

# Performance Flags
perf_df['Performance'] = ''
if not perf_df.empty:
    # Top 3 by ROAS
    top_roas = perf_df['ROAS'].nlargest(3).index
    perf_df.loc[top_roas, 'Performance'] = 'Top ROAS'
    # Underperformers: payout > 0, revenue == 0
    underperf = perf_df[(perf_df['total_payout'] > 0) & (perf_df['revenue'].fillna(0) == 0)].index
    perf_df.loc[underperf, 'Performance'] = 'No Revenue'
    # High payout, low ROAS
    low_roas = perf_df[(perf_df['total_payout'] > 0) & (perf_df['ROAS'] < 1)].index
    perf_df.loc[low_roas, 'Performance'] = perf_df.loc[low_roas, 'Performance'].replace('', 'Low ROAS')

# --- Influencer Performance Table ---
# Add Incremental ROAS calculation
baseline_per_user = 200
# Count unique users per influencer
user_counts = filtered_tracking.groupby('influencer_id')['user_id'].nunique().reset_index().rename(columns={'user_id':'unique_users','influencer_id':'ID'})
perf_df = perf_df.merge(user_counts, on='ID', how='left')
perf_df['baseline_revenue'] = perf_df['unique_users'].fillna(0) * baseline_per_user
perf_df['incremental_revenue'] = perf_df['revenue'] - perf_df['baseline_revenue']
perf_df['Incremental ROAS'] = perf_df['incremental_revenue'] / perf_df['total_payout']

# Update display columns
perf_display = perf_df[['name', 'category', 'platform', 'type', 'follower_count', 'reach', 'likes', 'comments', 'orders', 'revenue', 'total_payout', 'ROAS', 'Incremental ROAS', 'Performance']]
perf_display = perf_display.rename(columns={
    'name': 'Influencer',
    'category': 'Category',
    'platform': 'Platform',
    'type': 'Type',
    'follower_count': 'Followers',
    'reach': 'Reach',
    'likes': 'Likes',
    'comments': 'Comments',
    'orders': 'Orders',
    'revenue': 'Revenue',
    'total_payout': 'Payout',
    'ROAS': 'ROAS',
    'Incremental ROAS': 'Incremental ROAS',
    'Performance': 'Performance Flag'
})

# After filtering and before Key Insights and charts, always define engagement_df
if not posts.empty and not filtered_influencers.empty:
    filtered_posts = posts[posts['influencer_id'].isin(filtered_influencers['ID'])]
    if not filtered_posts.empty:
        engagement_df = filtered_posts.groupby('influencer_id').agg({'likes':'sum','comments':'sum','reach':'sum'}).reset_index()
        engagement_df['engagement_rate'] = (engagement_df['likes'] + engagement_df['comments']) / engagement_df['reach']
        revenue_per_inf = filtered_tracking.groupby('influencer_id')['revenue'].sum().reset_index()
        engagement_df = engagement_df.merge(revenue_per_inf, left_on='influencer_id', right_on='influencer_id', how='left')
        engagement_df = engagement_df.merge(influencers[['ID','name']], left_on='influencer_id', right_on='ID', how='left')

# --- KEY INSIGHTS SECTION ---
st.markdown('### 📌 Key Insights')

# Compute key insights
insight_lines = []
if not perf_display.empty:
    # Top-performing influencer by ROAS
    top_roas_row = perf_display.sort_values('ROAS', ascending=False).iloc[0]
    insight_lines.append(f"- Top-performing influencer: *{top_roas_row['Influencer']}* with ROAS of {top_roas_row['ROAS']:.2f}")
    # Platform with best engagement
    if not engagement_df.empty:
        eng_by_platform = filtered_influencers.merge(engagement_df, left_on='ID', right_on='influencer_id')
        eng_platform = eng_by_platform.groupby('platform')['engagement_rate'].mean().sort_values(ascending=False)
        if not eng_platform.empty:
            best_platform = eng_platform.index[0]
            avg_eng = eng_platform.iloc[0]*100
            insight_lines.append(f"- Platform with best engagement: *{best_platform}*, avg {avg_eng:.1f}%")
    # Poor ROI warning
    poor_roi_count = (perf_display['ROAS'] < 1).sum()
    insight_lines.append(f"- Poor ROI warning: *{poor_roi_count} influencers* with ROAS < 1")
else:
    insight_lines.append("- No data available for current filters.")
st.markdown("\n".join(insight_lines))

# --- KEY METRICS ---
st.header('Key Metrics')
col1, col2, col3, col4, col5 = st.columns(5)

total_revenue = filtered_tracking['revenue'].sum()
total_spend = filtered_payouts['total_payout'].sum()
total_orders = filtered_tracking['orders'].sum()
num_campaigns = filtered_tracking['campaign'].nunique()
avg_roas = total_revenue / total_spend if total_spend > 0 else 0

# Top Influencer by Revenue
if not filtered_tracking.empty:
    top_influencer_id = filtered_tracking.groupby('influencer_id')['revenue'].sum().idxmax()
    top_influencer_name = influencers[influencers['ID'] == top_influencer_id]['name'].values[0]
else:
    top_influencer_name = 'N/A'

col1.metric('Total Revenue', f"₹{total_revenue:,.0f}")
col2.metric('Total Spend', f"₹{total_spend:,.0f}")
col3.metric('Orders', f"{total_orders}")
col4.metric('Campaigns', f"{num_campaigns}")
col5.metric('Top Influencer', top_influencer_name)

# --- CHARTS ---
st.header('Performance Visualizations')

# Influencer vs ROAS (bar chart)
roas_df = filtered_tracking.groupby('influencer_id').agg({'revenue':'sum'}).join(
    filtered_payouts.set_index('influencer_id')['total_payout']
)
roas_df['ROAS'] = roas_df['revenue'] / roas_df['total_payout']
roas_df = roas_df.join(influencers.set_index('ID')['name'])
roas_df = roas_df.dropna(subset=['ROAS'])
if not roas_df.empty:
    fig1 = px.bar(roas_df, x='name', y='ROAS', title='Influencer vs ROAS', labels={'name':'Influencer'})
    st.plotly_chart(fig1, use_container_width=True)

# Engagement vs Revenue (scatter)
# Calculate engagement rate per influencer
# This block is now redundant as engagement_df is defined globally
# engagement_df = posts.groupby('influencer_id').agg({'likes':'sum','comments':'sum','reach':'sum'}).reset_index()
# engagement_df['engagement_rate'] = (engagement_df['likes'] + engagement_df['comments']) / engagement_df['reach']
# revenue_per_inf = filtered_tracking.groupby('influencer_id')['revenue'].sum().reset_index()
# engagement_df = engagement_df.merge(revenue_per_inf, left_on='influencer_id', right_on='influencer_id', how='left')
# engagement_df = engagement_df.merge(influencers[['ID','name']], left_on='influencer_id', right_on='ID', how='left')
if not engagement_df.empty:
    fig2 = px.scatter(engagement_df, x='engagement_rate', y='revenue', text='name',
                     title='Engagement Rate vs Revenue', labels={'engagement_rate':'Engagement Rate', 'revenue':'Revenue'})
    st.plotly_chart(fig2, use_container_width=True)

# Payout by Platform (pie chart)
payout_platform = filtered_influencers.merge(filtered_payouts, left_on='ID', right_on='influencer_id')
payout_platform = payout_platform.groupby('platform')['total_payout'].sum().reset_index()
if not payout_platform.empty:
    fig3 = px.pie(payout_platform, names='platform', values='total_payout', title='Payout by Platform')
    st.plotly_chart(fig3, use_container_width=True)

# Time-based revenue trend (line chart)
trend_df = filtered_tracking.copy()
trend_df['date'] = pd.to_datetime(trend_df['date'])
trend_df = trend_df.groupby('date')['revenue'].sum().reset_index()
if not trend_df.empty:
    fig4 = px.line(trend_df, x='date', y='revenue', title='Revenue Trend Over Time')
    st.plotly_chart(fig4, use_container_width=True)

# --- RAW DATA TABLES ---

st.header('Influencer Performance Table')

# Export button for influencer performance table
csv_perf = perf_display.to_csv(index=False).encode('utf-8')
st.download_button(
    label='Export Performance Table as CSV',
    data=csv_perf,
    file_name='influencer_performance.csv',
    mime='text/csv',
    key='export_perf_csv'
)

st.dataframe(perf_display.style.format({
    'Followers': '{:,.0f}',
    'Reach': '{:,.0f}',
    'Likes': '{:,.0f}',
    'Comments': '{:,.0f}',
    'Orders': '{:,.0f}',
    'Revenue': '₹{:,.0f}',
    'Payout': '₹{:,.0f}',
    'ROAS': '{:.2f}',
    'Incremental ROAS': '{:.2f}'
}))

# --- Incremental ROAS Chart ---
st.subheader('Influencer vs Incremental ROAS')
inc_roas_chart = perf_display.dropna(subset=['Incremental ROAS'])
if not inc_roas_chart.empty:
    fig_inc_roas = px.bar(inc_roas_chart, x='Influencer', y='Incremental ROAS', title='Influencer vs Incremental ROAS', labels={'Influencer':'Influencer'})
    st.plotly_chart(fig_inc_roas, use_container_width=True)

with st.expander('Show influencers.csv'):
    st.dataframe(filtered_influencers)
with st.expander('Show posts.csv'):
    st.dataframe(posts[posts['influencer_id'].isin(filtered_influencers['ID'])])
with st.expander('Show tracking_data.csv'):
    # Export button for filtered tracking data
    csv_tracking = filtered_tracking.to_csv(index=False).encode('utf-8')
    st.download_button(
        label='Export Filtered Tracking Data as CSV',
        data=csv_tracking,
        file_name='filtered_tracking_data.csv',
        mime='text/csv',
        key='export_tracking_csv'
    )
    st.dataframe(filtered_tracking)
with st.expander('Show payouts.csv'):
    st.dataframe(filtered_payouts) 