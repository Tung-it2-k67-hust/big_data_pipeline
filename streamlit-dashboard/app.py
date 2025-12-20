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

# Page configuration
st.set_page_config(
    page_title="Football Data Analytics Dashboard",
    page_icon="⚽",
    layout="wide"
)

# Connect to Elasticsearch
@st.cache_resource
def get_es_connection():
    """Create Elasticsearch connection"""
    es_host = os.getenv('ELASTICSEARCH_HOST', 'elasticsearch')
    es_port = int(os.getenv('ELASTICSEARCH_PORT', '9200'))
    return Elasticsearch([{'host': es_host, 'port': es_port, 'scheme': 'http'}])

def fetch_data(es, index='football-matches', size=10000):
    """Fetch data from Elasticsearch"""
    try:
        # Fetch a larger dataset for historical analysis
        query = {
            "size": size,
            "sort": [{"match_date": {"order": "desc"}}],
            "query": {
                "match_all": {}
            }
        }
        response = es.search(index=index, body=query)
        hits = response['hits']['hits']
        data = [hit['_source'] for hit in hits]
        return pd.DataFrame(data)
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
    
    # Connect to Elasticsearch
    es = get_es_connection()
    
    # Fetch data
    with st.spinner('Fetching data from Elasticsearch...'):
        df = fetch_data(es)
    
    if df.empty:
        st.warning("No data available. Make sure the pipeline is running and data is being ingested.")
        if auto_refresh:
            time.sleep(refresh_interval)
            st.rerun()
        return

    # Ensure date column is datetime
    if 'match_date' in df.columns:
        df['match_date'] = pd.to_datetime(df['match_date'])
    elif 'Date' in df.columns:
        df['match_date'] = pd.to_datetime(df['Date'], errors='coerce')

    # Ensure numeric columns exist (fill with 0 if missing)
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
            df[col] = df[col].fillna(0)

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
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Matches per Month (Heatmap)")
            if 'match_date' in df.columns:
                if 'Year' not in df.columns:
                    df['Year'] = df['match_date'].dt.year
                if 'Month' not in df.columns:
                    df['Month'] = df['match_date'].dt.month
                
                matches_per_month = df.groupby(['Year', 'Month']).size().reset_index(name='Count')
                heatmap_data = matches_per_month.pivot(index='Month', columns='Year', values='Count')
                
                fig_heat = px.imshow(heatmap_data, 
                                labels=dict(x="Year", y="Month", color="Matches"),
                                aspect="auto", color_continuous_scale="Viridis")
                fig_heat.update_yaxes(tickmode='linear', tick0=1, dtick=1)
                st.plotly_chart(fig_heat, use_container_width=True)

        with col2:
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
        if 'match_date' in df.columns:
            daily_shots = df.groupby('match_date')[['hs', 'as', 'hst', 'ast']].sum().reset_index()
            fig_shots = go.Figure()
            fig_shots.add_trace(go.Scatter(x=daily_shots['match_date'], y=daily_shots['hs'], mode='lines', name='Home Shots'))
            fig_shots.add_trace(go.Scatter(x=daily_shots['match_date'], y=daily_shots['as'], mode='lines', name='Away Shots'))
            fig_shots.add_trace(go.Scatter(x=daily_shots['match_date'], y=daily_shots['hst'], mode='lines', name='Home On Target', line=dict(dash='dot')))
            fig_shots.add_trace(go.Scatter(x=daily_shots['match_date'], y=daily_shots['ast'], mode='lines', name='Away On Target', line=dict(dash='dot')))
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
        
        if 'psh' in df.columns and 'match_date' in df.columns:
            # Filter out 0 values which might be missing data
            odds_df = df[(df['psh'] > 0) & (df['psd'] > 0) & (df['psa'] > 0)]
            
            if not odds_df.empty:
                daily_odds = odds_df.groupby('match_date')[['psh', 'psd', 'psa']].mean().reset_index()
                
                fig_odds = go.Figure()
                fig_odds.add_trace(go.Scatter(x=daily_odds['match_date'], y=daily_odds['psh'], name='Home Win Odds (PSH)'))
                fig_odds.add_trace(go.Scatter(x=daily_odds['match_date'], y=daily_odds['psd'], name='Draw Odds (PSD)'))
                fig_odds.add_trace(go.Scatter(x=daily_odds['match_date'], y=daily_odds['psa'], name='Away Win Odds (PSA)'))
                
                fig_odds.update_layout(xaxis_title='Date', yaxis_title='Average Odds', hovermode="x unified")
                st.plotly_chart(fig_odds, use_container_width=True)
            else:
                st.info("No betting odds data available to plot.")
        else:
            st.error("Betting odds columns (PSH, PSD, PSA) not found.")

    # --- TAB 5: RAW DATA ---
    with tab5:
        st.header("Raw Data")
        st.dataframe(df.head(100), use_container_width=True)
    
    # Auto-refresh logic
    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()

if __name__ == '__main__':
    main()
