"""
Streamlit Dashboard for Football Match Data Visualization
Real-time analytics and visualizations from Elasticsearch
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from elasticsearch import Elasticsearch
from datetime import datetime, timedelta
import time
import os
try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st_autorefresh = None

# Page configuration
st.set_page_config(
    page_title="Football Data Analytics Dashboard",
    page_icon="⚽",
    layout="wide"
)

# Connect to Elasticsearch
@st.cache_resource
def get_es_connection():
    """Create Elasticsearch connection with retry logic"""
    es_host = os.getenv('ELASTICSEARCH_HOST', 'elasticsearch')
    es_port = int(os.getenv('ELASTICSEARCH_PORT', '9200'))
    
    # Elasticsearch 8.x client configuration
    es = Elasticsearch(
        f"http://{es_host}:{es_port}",
        request_timeout=30,
        max_retries=10,
        retry_on_timeout=True
    )
    
    # Retry connecting up to 10 times with wait time
    max_attempts = 10
    for i in range(max_attempts):
        try:
            if es.ping():
                return es
            else:
                st.warning(f"Elasticsearch ping failed (Attempt {i+1}/{max_attempts}). Service might be starting...")
        except Exception as e:
            st.warning(f"Connecting to Elasticsearch... (Attempt {i+1}/{max_attempts}). Error: {str(e)}")
        
        time.sleep(10) # Wait 10 seconds before retrying
            
    st.error("Failed to connect to Elasticsearch after multiple attempts. Please check if the service is running and accessible.")
    return None

def fetch_data(es, index='football-matches', max_size=10000):
    """
    Fetch data from Elasticsearch
    Increased max_size to 10000 to show more records.
    """
    try:
        # First, get the total count with timeout
        # Updated for Elasticsearch 8.x client (query instead of body)
        count_response = es.count(index=index, query={"match_all": {}})
        total_docs = count_response['count']
        
        # Fetch up to max_size
        fetch_size = min(total_docs, max_size)
        
        # Updated for Elasticsearch 8.x client
        response = es.search(
            index=index, 
            query={"match_all": {}},
            sort=[{"date": {"order": "desc"}}],
            size=fetch_size,
            request_timeout=60
        )
        
        hits = response['hits']['hits']
        data = [hit['_source'] for hit in hits]
        df = pd.DataFrame(data)
        
        # Add metadata about total available records
        df.attrs['total_in_es'] = total_docs
        df.attrs['fetched'] = len(df)
        
        return df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

def main():
    """Main dashboard function"""
    st.title("⚽ Football Data Analytics Dashboard")
    st.markdown("Real-time analytics and visualization pipeline")
    
    # Sidebar
    st.sidebar.header("Dashboard Controls")
    auto_refresh = st.sidebar.checkbox("Auto Refresh", value=False)
    refresh_interval = st.sidebar.slider("Refresh Interval (seconds)", 5, 60, 30)
    
    if auto_refresh and st_autorefresh:
        st_autorefresh(interval=refresh_interval * 1000, key="data_refresh")
    elif auto_refresh and st_autorefresh is None:
        st.warning("streamlit-autorefresh not installed. Falling back to manual refresh.")

    # Connect to Elasticsearch
    es = get_es_connection()
    
    # Stop execution if connection failed
    if es is None:
        st.stop()
    
    # Fetch data
    with st.spinner('Fetching data from Elasticsearch...'):
        df = fetch_data(es)
    
    if df.empty:
        st.warning("No data available. Make sure the pipeline is running and data is being ingested.")
        # Removed blocking sleep
        return

    # Ensure date column is datetime (keep original 'date' field in format yyyy-mm-dd)
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
    
    # Check if columns exist (fill with 0 if missing)
    # Added: hc, ac (corners), hr, ar (red cards), psh, psd, psa (odds)
    numeric_cols = [
        'hs', 'as', 'hst', 'ast', 'fthg', 'ftag', 
        'hy', 'ay', 'hf', 'af', 'hc', 'ac', 'hr', 'ar',
        'psh', 'psd', 'psa'
    ]
    for col in numeric_cols:
        if col not in df.columns:
            df[col] = 0
        else:
            # Force conversion to numeric, coercing errors to NaN then filling with 0
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Create tabs for the requested visualizations
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Overview & Results", 
        "Attack Stats (Shots/Corners)", 
        "Discipline (Fouls/Cards)", 
        "Betting Market",
        "Raw Data"
    ])
    
    # --- TAB 1: OVERVIEW & RESULTS ---
    with tab1:
        st.subheader("Match Result Distribution")
        if 'ftr' in df.columns:
            ftr_counts = df['ftr'].value_counts().reset_index()
            ftr_counts.columns = ['Result', 'Count']
            # Map codes to names
            ftr_counts['Result Name'] = ftr_counts['Result'].map({'H': 'Home Win', 'A': 'Away Win', 'D': 'Draw'})
            
            fig_pie = px.pie(ftr_counts, values='Count', names='Result Name', 
                         color='Result Name',
                         color_discrete_map={'Home Win':'#1f77b4', 'Away Win':'#ff7f0e', 'Draw':'#2ca02c'})
            st.plotly_chart(fig_pie, use_container_width=True)

    # --- TAB 2: ATTACK STATS ---
    with tab2:
        st.subheader("Daily Shots Activity")
        if 'date' in df.columns:
            daily_shots = df.groupby('date')[['hs', 'as', 'hst', 'ast']].sum().reset_index()
            fig_shots = go.Figure()
            fig_shots.add_trace(go.Scatter(x=daily_shots['date'], y=daily_shots['hs'], mode='lines', name='Home Shots'))
            fig_shots.add_trace(go.Scatter(x=daily_shots['date'], y=daily_shots['as'], mode='lines', name='Away Shots'))
            fig_shots.add_trace(go.Scatter(x=daily_shots['date'], y=daily_shots['hst'], mode='lines', name='Home On Target', line=dict(dash='dot')))
            fig_shots.add_trace(go.Scatter(x=daily_shots['date'], y=daily_shots['ast'], mode='lines', name='Away On Target', line=dict(dash='dot')))
            fig_shots.update_layout(xaxis_title='Date', yaxis_title='Count', hovermode="x unified")
            st.plotly_chart(fig_shots, use_container_width=True)

        st.divider()
        
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.subheader("Average Goals: Home vs Away")
            avg_goals = df[['fthg', 'ftag']].mean().reset_index()
            avg_goals.columns = ['Type', 'Average']
            avg_goals['Type'] = avg_goals['Type'].replace({'fthg': 'Home Goals', 'ftag': 'Away Goals'})
            fig_goals = px.bar(avg_goals, x='Type', y='Average', color='Type', text_auto='.2f')
            st.plotly_chart(fig_goals, use_container_width=True)
            
        with col_c2:
            st.subheader("Average Corners: Home vs Away")
            if 'hc' in df.columns and 'ac' in df.columns:
                avg_corners = df[['hc', 'ac']].mean().reset_index()
                avg_corners.columns = ['Type', 'Average']
                avg_corners['Type'] = avg_corners['Type'].replace({'hc': 'Home Corners', 'ac': 'Away Corners'})
                fig_corners = px.bar(avg_corners, x='Type', y='Average', color='Type', text_auto='.2f',
                                     color_discrete_sequence=['#9467bd', '#8c564b'])
                st.plotly_chart(fig_corners, use_container_width=True)

    # --- TAB 3: DISCIPLINE ---
    with tab3:
        st.subheader("Fouls vs Yellow Cards Correlation")
        if 'hy' in df.columns and 'hf' in df.columns and 'af' in df.columns:
            fouls_by_hy = df.groupby('hy')[['hf', 'af']].mean().reset_index()
            fouls_melted = fouls_by_hy.melt(id_vars=['hy'], value_vars=['hf', 'af'], 
                                            var_name='Foul Type', value_name='Average Fouls')
            fig_fouls = px.bar(fouls_melted, x='hy', y='Average Fouls', color='Foul Type', barmode='group',
                         labels={'hy': 'Home Yellow Cards', 'Average Fouls': 'Mean Fouls'})
            st.plotly_chart(fig_fouls, use_container_width=True)
            
        st.divider()
        st.subheader("Red Cards Analysis")
        if 'hr' in df.columns and 'ar' in df.columns:
            # Sum of red cards over time (cumulative or total) - Let's show total distribution
            total_reds = df[['hr', 'ar']].sum().reset_index()
            total_reds.columns = ['Type', 'Total Count']
            total_reds['Type'] = total_reds['Type'].replace({'hr': 'Home Red Cards', 'ar': 'Away Red Cards'})
            fig_reds = px.pie(total_reds, values='Total Count', names='Type', 
                              title="Total Red Cards Distribution", hole=0.4,
                              color_discrete_sequence=['#d62728', '#ff9896'])
            st.plotly_chart(fig_reds, use_container_width=True)

    # --- TAB 4: BETTING MARKET ---
    with tab4:
        st.subheader("Betting Odds Trends (Pinnacle)")
        st.markdown("Average daily odds for Home Win (PSH), Draw (PSD), and Away Win (PSA).")
        
        if 'psh' in df.columns and 'date' in df.columns:
            # Filter out 0 values which might be missing data
            odds_df = df[(df['psh'] > 0) & (df['psd'] > 0) & (df['psa'] > 0)]
            
            if not odds_df.empty:
                daily_odds = odds_df.groupby('date')[['psh', 'psd', 'psa']].mean().reset_index()
                
                fig_odds = go.Figure()
                fig_odds.add_trace(go.Scatter(x=daily_odds['date'], y=daily_odds['psh'], name='Home Win Odds (PSH)'))
                fig_odds.add_trace(go.Scatter(x=daily_odds['date'], y=daily_odds['psd'], name='Draw Odds (PSD)'))
                fig_odds.add_trace(go.Scatter(x=daily_odds['date'], y=daily_odds['psa'], name='Away Win Odds (PSA)'))
                
                fig_odds.update_layout(xaxis_title='Date', yaxis_title='Average Odds', hovermode="x unified")
                st.plotly_chart(fig_odds, use_container_width=True)
            else:
                st.info("No betting odds data available to plot.")
        else:
            st.error("Betting odds columns (PSH, PSD, PSA) not found.")

    # --- TAB 5: RAW DATA ---
    with tab5:
        st.header("Raw Data")
        
        # Show total records with clarification
        total_in_es = df.attrs.get('total_in_es', len(df))
        fetched = len(df)
        
        if total_in_es > fetched:
            st.info(f"📊 **Total Records in Elasticsearch:** {total_in_es:,} | **Displayed:** {fetched:,} (Elasticsearch query limit)")
            st.caption("💡 Note: Elasticsearch has a default limit of 10,000 documents per query. All data is stored, but only the most recent 10,000 are shown here for performance.")
        else:
            st.write(f"**Total Records:** {len(df):,}")
        
        # Add pagination controls
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            page_size = st.selectbox("Rows per page", [50, 100, 200, 500, 1000], index=1)
        with col2:
            total_pages = (len(df) - 1) // page_size + 1
            page_number = st.number_input(f"Page (1-{total_pages})", min_value=1, max_value=total_pages, value=1)
        
        # Calculate start and end indices
        start_idx = (page_number - 1) * page_size
        end_idx = min(start_idx + page_size, len(df))
        
        # Display paginated data
        st.write(f"Showing records {start_idx + 1} to {end_idx} of {len(df):,}")
        st.dataframe(df.iloc[start_idx:end_idx], use_container_width=True, height=600)
    
    # Auto-refresh logic
    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()

if __name__ == '__main__':
    main()
