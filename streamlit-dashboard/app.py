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

    # Create tabs for the requested visualizations
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Overview & Matches per Month", 
        "Shots Analysis", 
        "Goals Analysis", 
        "Fouls vs Yellow Cards",
        "Raw Data"
    ])
    
    # 1. Tổng quan về số các trận đấu theo từng tháng trong các năm
    with tab1:
        st.header("1. Matches Overview by Month and Year")
        st.markdown("Heatmap of matches per month over years.")
        
        if 'match_date' in df.columns:
            # Extract Month and Year if not present (though Spark should have added them)
            if 'Year' not in df.columns:
                df['Year'] = df['match_date'].dt.year
            if 'Month' not in df.columns:
                df['Month'] = df['match_date'].dt.month
            
            # Group by Year and Month
            matches_per_month = df.groupby(['Year', 'Month']).size().reset_index(name='Count')
            
            # Pivot for heatmap
            heatmap_data = matches_per_month.pivot(index='Month', columns='Year', values='Count')
            
            fig = px.imshow(heatmap_data, 
                            labels=dict(x="Year", y="Month", color="Number of Matches"),
                            x=heatmap_data.columns,
                            y=heatmap_data.index,
                            title="Heatmap of Matches per Month over Years",
                            aspect="auto")
            fig.update_yaxes(tickmode='linear', tick0=1, dtick=1)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("Date column not found for analysis.")

    # 2. Số lượng cú sút và cú sút trúng đích của đội chủ nhà và đội khách theo ngày thi đấu
    with tab2:
        st.header("2. Shots Analysis (Time Series)")
        st.markdown("Time Series Analysis of Home/Away Shots (HS/AS) and Shots on Target (HST/AST).")
        
        if 'match_date' in df.columns:
            # Aggregate by Date (sum or mean) - User suggested sum or mean if dense
            # Let's use sum per day
            daily_shots = df.groupby('match_date')[['HS', 'AS', 'HST', 'AST']].sum().reset_index()
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=daily_shots['match_date'], y=daily_shots['HS'], mode='lines', name='Home Shots (HS)'))
            fig.add_trace(go.Scatter(x=daily_shots['match_date'], y=daily_shots['AS'], mode='lines', name='Away Shots (AS)'))
            fig.add_trace(go.Scatter(x=daily_shots['match_date'], y=daily_shots['HST'], mode='lines', name='Home Shots Target (HST)', line=dict(dash='dash')))
            fig.add_trace(go.Scatter(x=daily_shots['match_date'], y=daily_shots['AST'], mode='lines', name='Away Shots Target (AST)', line=dict(dash='dash')))
            
            fig.update_layout(title='Daily Shots Statistics', xaxis_title='Date', yaxis_title='Count')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("Date column not found for analysis.")

    # 3. Số bàn thắng trung bình được ghi của đội nhà và đội khách
    with tab3:
        st.header("3. Average Goals Analysis")
        st.markdown("Comparison of Average Home Goals (FTHG) vs Average Away Goals (FTAG).")
        
        avg_goals = df[['FTHG', 'FTAG']].mean().reset_index()
        avg_goals.columns = ['Type', 'Average Goals']
        # Rename for better display
        avg_goals['Type'] = avg_goals['Type'].replace({'FTHG': 'Home Team Goals', 'FTAG': 'Away Team Goals'})
        
        fig = px.bar(avg_goals, x='Type', y='Average Goals', color='Type',
                     title="Average Goals: Home vs Away",
                     text_auto='.2f')
        st.plotly_chart(fig, use_container_width=True)

    # 4. Số lượt phạm lỗi trung bình của các đội theo số lượng thẻ vàng của đội chủ nhà
    with tab4:
        st.header("4. Fouls vs Home Yellow Cards Analysis")
        st.markdown("Average Fouls (HF/AF) grouped by Home Yellow Cards (HY).")
        
        if 'HY' in df.columns and 'HF' in df.columns and 'AF' in df.columns:
            fouls_by_hy = df.groupby('HY')[['HF', 'AF']].mean().reset_index()
            
            # Melt for easier plotting with Plotly Express
            fouls_melted = fouls_by_hy.melt(id_vars=['HY'], value_vars=['HF', 'AF'], 
                                            var_name='Foul Type', value_name='Average Fouls')
            
            fig = px.bar(fouls_melted, x='HY', y='Average Fouls', color='Foul Type', barmode='group',
                         labels={'HY': 'Home Yellow Cards (HY)', 'Average Fouls': 'Mean Fouls'},
                         title="Correlation between Home Yellow Cards and Average Fouls")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("Required columns (HY, HF, AF) not found.")

    # Raw Data Tab
    with tab5:
        st.header("Raw Data")
        st.dataframe(df.head(100), use_container_width=True)
    
    # Auto-refresh logic
    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()

if __name__ == '__main__':
    main()
