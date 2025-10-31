"""
Streamlit Dashboard for Big Data Pipeline Visualization
Real-time analytics and visualizations from Elasticsearch
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from elasticsearch import Elasticsearch
from datetime import datetime, timedelta
import time

# Page configuration
st.set_page_config(
    page_title="Big Data Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# Connect to Elasticsearch
@st.cache_resource
def get_es_connection():
    """Create Elasticsearch connection"""
    import os
    es_host = os.getenv('ELASTICSEARCH_HOST', 'elasticsearch')
    es_port = int(os.getenv('ELASTICSEARCH_PORT', '9200'))
    return Elasticsearch([{'host': es_host, 'port': es_port, 'scheme': 'http'}])

def fetch_recent_events(es, index='events', size=1000):
    """Fetch recent events from Elasticsearch"""
    try:
        query = {
            "size": size,
            "sort": [{"timestamp": {"order": "desc"}}],
            "query": {
                "range": {
                    "timestamp": {
                        "gte": "now-1h"
                    }
                }
            }
        }
        response = es.search(index=index, body=query)
        hits = response['hits']['hits']
        data = [hit['_source'] for hit in hits]
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

def fetch_aggregated_data(es, index='events-aggregated', size=500):
    """Fetch aggregated data from Elasticsearch"""
    try:
        query = {
            "size": size,
            "sort": [{"window.start": {"order": "desc"}}]
        }
        response = es.search(index=index, body=query)
        hits = response['hits']['hits']
        data = [hit['_source'] for hit in hits]
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Error fetching aggregated data: {e}")
        return pd.DataFrame()

def main():
    """Main dashboard function"""
    st.title("📊 Big Data Analytics Dashboard")
    st.markdown("Real-time analytics and visualization pipeline")
    
    # Sidebar
    st.sidebar.header("Dashboard Controls")
    auto_refresh = st.sidebar.checkbox("Auto Refresh", value=True)
    refresh_interval = st.sidebar.slider("Refresh Interval (seconds)", 5, 60, 10)
    
    # Connect to Elasticsearch
    es = get_es_connection()
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Event Analysis", "Revenue Analysis", "Real-time Stream"])
    
    # Fetch data
    df = fetch_recent_events(es)
    
    if df.empty:
        st.warning("No data available. Make sure the pipeline is running.")
        return
    
    # Overview Tab
    with tab1:
        st.header("System Overview")
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Events", len(df))
        
        with col2:
            if 'revenue' in df.columns:
                total_revenue = df['revenue'].sum()
                st.metric("Total Revenue", f"${total_revenue:,.2f}")
        
        with col3:
            if 'event_type' in df.columns:
                unique_events = df['event_type'].nunique()
                st.metric("Event Types", unique_events)
        
        with col4:
            if 'region' in df.columns:
                regions = df['region'].nunique()
                st.metric("Regions", regions)
        
        # Event distribution over time
        if 'timestamp' in df.columns:
            st.subheader("Event Distribution Over Time")
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            time_series = df.set_index('timestamp').resample('1T').size()
            fig = px.line(time_series, title="Events per Minute")
            st.plotly_chart(fig, use_container_width=True)
    
    # Event Analysis Tab
    with tab2:
        st.header("Event Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'event_type' in df.columns:
                st.subheader("Events by Type")
                event_counts = df['event_type'].value_counts()
                fig = px.pie(values=event_counts.values, names=event_counts.index, 
                           title="Event Type Distribution")
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if 'region' in df.columns:
                st.subheader("Events by Region")
                region_counts = df['region'].value_counts()
                fig = px.bar(x=region_counts.index, y=region_counts.values,
                           labels={'x': 'Region', 'y': 'Count'},
                           title="Events by Region")
                st.plotly_chart(fig, use_container_width=True)
        
        if 'device' in df.columns:
            st.subheader("Device Distribution")
            device_counts = df['device'].value_counts()
            fig = px.bar(x=device_counts.index, y=device_counts.values,
                       labels={'x': 'Device', 'y': 'Count'},
                       title="Events by Device")
            st.plotly_chart(fig, use_container_width=True)
    
    # Revenue Analysis Tab
    with tab3:
        st.header("Revenue Analysis")
        
        if 'revenue' in df.columns and 'region' in df.columns:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Revenue by Region")
                revenue_by_region = df.groupby('region')['revenue'].sum().sort_values(ascending=False)
                fig = px.bar(x=revenue_by_region.index, y=revenue_by_region.values,
                           labels={'x': 'Region', 'y': 'Revenue ($)'},
                           title="Total Revenue by Region")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("Revenue by Event Type")
                revenue_by_event = df.groupby('event_type')['revenue'].sum().sort_values(ascending=False)
                fig = px.bar(x=revenue_by_event.index, y=revenue_by_event.values,
                           labels={'x': 'Event Type', 'y': 'Revenue ($)'},
                           title="Total Revenue by Event Type")
                st.plotly_chart(fig, use_container_width=True)
        
        if 'price' in df.columns:
            st.subheader("Price Distribution")
            fig = px.histogram(df, x='price', nbins=50, title="Price Distribution")
            st.plotly_chart(fig, use_container_width=True)
    
    # Real-time Stream Tab
    with tab4:
        st.header("Real-time Event Stream")
        st.subheader("Latest Events")
        
        # Display recent events
        display_cols = ['timestamp', 'user_id', 'event_type', 'product_id', 'price', 'quantity', 'region', 'device']
        display_cols = [col for col in display_cols if col in df.columns]
        st.dataframe(df[display_cols].head(50), use_container_width=True)
    
    # Auto-refresh
    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()

if __name__ == '__main__':
    main()
