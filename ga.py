import streamlit as st
import pandas as pd
import altair as alt
import numpy as np

# --- 1. CONFIGURATION AND DATA LOADING ---
st.set_page_config(
    page_title="Indian Budget Analysis Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Function to load and clean the data
@st.cache_data
def load_and_clean_data(file_path):
    # Load the data
    df = pd.read_csv(file_path)

    # List of financial columns that may contain non-numeric data (like '-')
    finance_cols = [
        'Revenue (Plan)', 'Capital (Plan)', 'Total (Plan)',
        'Revenue (Non-Plan)', 'Capital (Non-Plan)', 'Total (Non-Plan)',
        'Total Plan & Non-Plan'
    ]

    # Convert non-numeric values (like '-') to NaN and then to float, filling NaN with 0
    for col in finance_cols:
        # Replace common non-numeric separators/placeholders with NaN
        df[col] = df[col].replace({'-': np.nan, 'NA': np.nan})
        # Coerce to numeric, setting errors='coerce' to turn any remaining non-numeric into NaN
        df[col] = pd.to_numeric(df[col], errors='coerce')
        # Fill NaN (original or coerced) with 0
        df[col] = df[col].fillna(0)
    
    # Extract the starting year from the 'Year' column (e.g., '2014-2015' -> 2014)
    df['Start Year'] = df['Year'].apply(lambda x: int(x.split('-')[0]))
    
    # Create a column for Total Budget
    df['Total Budget (INR Cr)'] = df['Total Plan & Non-Plan']
    
    return df

# Attempt to load the data
file_path = "Budget.csv"
try:
    df = load_and_clean_data(file_path)
    # Get a list of unique ministries for the sidebar filter
    all_ministries = ['All Ministries'] + sorted(df['Ministry Name'].unique().tolist())
    all_years = ['All Years'] + sorted(df['Start Year'].unique().tolist())
    st.sidebar.success(f"Data loaded successfully!")

except Exception as e:
    st.error(f"Could not load or process the CSV file: {e}")
    st.stop()


# --- 2. SIDEBAR FILTERS ---
st.sidebar.title("Dashboard Filters")
st.sidebar.markdown("---")

# Ministry Filter
selected_ministry = st.sidebar.selectbox(
    "Select Ministry:",
    all_ministries
)

# Year Filter
selected_year = st.sidebar.selectbox(
    "Select Financial Year:",
    all_years
)

# Apply filters
df_filtered = df.copy()

if selected_ministry != 'All Ministries':
    df_filtered = df_filtered[df_filtered['Ministry Name'] == selected_ministry]

if selected_year != 'All Years':
    df_filtered = df_filtered[df_filtered['Start Year'] == selected_year]


# --- 3. MAIN DASHBOARD UI ---
st.title("💰 Indian Budget Visualizer")
st.markdown(f"**Viewing Data for:** **{selected_ministry}** in **{selected_year}**")
st.markdown("---")


# --- 4. KEY METRICS ---
if not df_filtered.empty:
    
    # Calculate totals for the selected filters
    total_budget = df_filtered['Total Budget (INR Cr)'].sum()
    total_plan = df_filtered['Total (Plan)'].sum()
    total_non_plan = df_filtered['Total (Non-Plan)'].sum()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Total Budget (All Time/Filtered)",
            value=f"₹ {total_budget:,.2f} Cr"
        )

    with col2:
        st.metric(
            label="Total Plan Expenditure",
            value=f"₹ {total_plan:,.2f} Cr"
        )
        
    with col3:
        st.metric(
            label="Total Non-Plan Expenditure",
            value=f"₹ {total_non_plan:,.2f} Cr"
        )

st.markdown("---")


# --- 5. VISUALIZATIONS AND TABS ---

tab1, tab2, tab3 = st.tabs(["📊 Budget Trends Over Time", "📋 Ministry/Year Breakdown", "🔍 Raw Data"])

with tab1:
    st.header("Budget Trend Analysis")
    st.caption("Shows how the total budget has changed over the years.")
    
    # Group by year for trend analysis
    df_trend = df.groupby('Start Year')['Total Budget (INR Cr)'].sum().reset_index()
    
    # Line Chart
    trend_chart = alt.Chart(df_trend).mark_line(point=True).encode(
        x=alt.X('Start Year:O', title='Financial Year (Start)'),
        y=alt.Y('Total Budget (INR Cr)', title='Total Budget (INR Crore)'),
        tooltip=['Start Year', alt.Tooltip('Total Budget (INR Cr)', format=',.2f')]
    ).properties(
        title="Total Budget of All Ministries Over Time"
    ).interactive() # Make the chart zoomable/pannable
    
    st.altair_chart(trend_chart, use_container_width=True)

    
with tab2:
    st.header("Detailed Budget Breakdown")
    
    if selected_year != 'All Years':
        st.subheader(f"Budget Distribution for Year {selected_year}")
        
        # Prepare data for ministry breakdown (only for a single selected year)
        df_year_breakdown = df_filtered.sort_values('Total Budget (INR Cr)', ascending=False).head(10)
        
        breakdown_chart = alt.Chart(df_year_breakdown).mark_bar().encode(
            x=alt.X('Total Budget (INR Cr)', title='Total Budget (INR Crore)'),
            y=alt.Y('Ministry Name', sort='-x', title='Ministry'),
            color=alt.Color('Ministry Name', legend=None),
            tooltip=['Ministry Name', alt.Tooltip('Total Budget (INR Cr)', format=',.2f')]
        ).properties(
            title=f"Top Ministries by Budget in {selected_year}"
        ).interactive()
        
        st.altair_chart(breakdown_chart, use_container_width=True)

    elif selected_ministry != 'All Ministries':
        st.subheader(f"Plan vs. Non-Plan Expenditure for {selected_ministry}")

        # Data for stacked bar chart (Plan vs Non-Plan)
        df_plan_nonplan = df_filtered[['Start Year', 'Total (Plan)', 'Total (Non-Plan)']].melt(
            id_vars=['Start Year'], 
            value_vars=['Total (Plan)', 'Total (Non-Plan)'],
            var_name='Type',
            value_name='Amount'
        )

        stacked_chart = alt.Chart(df_plan_nonplan).mark_bar().encode(
            x=alt.X('Start Year:O', title='Financial Year (Start)'),
            y=alt.Y('Amount', title='Amount (INR Crore)'),
            color='Type',
            tooltip=['Start Year', 'Type', alt.Tooltip('Amount', format=',.2f')]
        ).properties(
            title=f"Plan vs. Non-Plan Expenditure for {selected_ministry}"
        ).interactive()

        st.altair_chart(stacked_chart, use_container_width=True)

    else:
        st.info("Select a specific **Year** or **Ministry** in the sidebar to view a detailed breakdown chart.")


with tab3:
    st.header("Raw Data Table")
    st.markdown("The complete, cleaned dataset for inspection.")
    st.dataframe(df, use_container_width=True)
