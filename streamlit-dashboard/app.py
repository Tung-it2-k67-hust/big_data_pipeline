"""
Streamlit Dashboard cho Trực quan hóa Dữ liệu Bóng đá
Phân tích và hiển thị thời gian thực từ Elasticsearch
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

# Cấu hình trang
st.set_page_config(
    page_title="Dashboard Phân Tích Bóng Đá",
    page_icon="⚽",
    layout="wide"
)

# Kết nối đến Elasticsearch
@st.cache_resource
def get_es_connection():
    """Tạo kết nối Elasticsearch với cơ chế thử lại"""
    es_host = os.getenv('ELASTICSEARCH_HOST', 'elasticsearch')
    es_port = int(os.getenv('ELASTICSEARCH_PORT', '9200'))
    
    # Cấu hình client Elasticsearch 8.x
    es = Elasticsearch(
        f"http://{es_host}:{es_port}",
        request_timeout=30,
        max_retries=10,
        retry_on_timeout=True
    )
    
    # Thử kết nối tối đa 10 lần
    max_attempts = 10
    for i in range(max_attempts):
        try:
            if es.ping():
                return es
            else:
                st.warning(f"Ping Elasticsearch thất bại (Lần {i+1}/{max_attempts}). Dịch vụ có thể đang khởi động...")
        except Exception as e:
            st.warning(f"Đang kết nối Elasticsearch... (Lần {i+1}/{max_attempts}). Lỗi: {str(e)}")
        
        time.sleep(10) # Đợi 10 giây trước khi thử lại
            
    st.error("Không thể kết nối đến Elasticsearch sau nhiều lần thử. Vui lòng kiểm tra dịch vụ.")
    return None

def fetch_data(es, index='football-matches', max_size=10000):
    """
    Lấy dữ liệu từ Elasticsearch
    Tăng max_size lên 10000 để hiển thị nhiều bản ghi hơn.
    """
    try:
        # Lấy tổng số lượng bản ghi
        count_response = es.count(index=index, query={"match_all": {}})
        total_docs = count_response['count']
        
        # Lấy tối đa max_size bản ghi
        fetch_size = min(total_docs, max_size)
        
        # Query dữ liệu, sắp xếp theo ngày giảm dần
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
        
        # Thêm metadata về tổng số bản ghi
        df.attrs['total_in_es'] = total_docs
        df.attrs['fetched'] = len(df)
        
        return df
    except Exception as e:
        st.error(f"Lỗi khi lấy dữ liệu: {e}")
        return pd.DataFrame()

def main():
    """Hàm chính của Dashboard"""
    st.title("⚽ Dashboard Phân Tích Dữ Liệu Bóng Đá")
    st.markdown("Hệ thống phân tích và trực quan hóa dữ liệu thời gian thực")
    
    # Sidebar điều khiển
    st.sidebar.header("Điều Khiển")
    auto_refresh = st.sidebar.checkbox("Tự động làm mới", value=False)
    refresh_interval = st.sidebar.slider("Chu kỳ làm mới (giây)", 5, 60, 30)
    
    if auto_refresh and st_autorefresh:
        st_autorefresh(interval=refresh_interval * 1000, key="data_refresh")
    elif auto_refresh and st_autorefresh is None:
        st.warning("Chưa cài đặt streamlit-autorefresh. Chuyển sang làm mới thủ công.")

    # Kết nối Elasticsearch
    es = get_es_connection()
    
    # Dừng nếu không kết nối được
    if es is None:
        st.stop()
    
    # Lấy dữ liệu
    with st.spinner('Đang tải dữ liệu từ Elasticsearch...'):
        df = fetch_data(es)
    
    if df.empty:
        st.warning("Chưa có dữ liệu. Hãy đảm bảo pipeline đang chạy và dữ liệu đang được đẩy vào.")
        return

    # Chuyển đổi cột date sang datetime
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
    
    # Xử lý các cột số (điền 0 nếu thiếu)
    numeric_cols = [
        'hs', 'as', 'hst', 'ast', 'fthg', 'ftag', 
        'hy', 'ay', 'hf', 'af', 'hc', 'ac', 'hr', 'ar',
        'psh', 'psd', 'psa'
    ]
    for col in numeric_cols:
        if col not in df.columns:
            df[col] = 0
        else:
            # Ép kiểu sang số, lỗi thành NaN rồi điền 0
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Tạo các tab hiển thị
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Tổng Quan & Kết Quả", 
        "Thống Kê Tấn Công", 
        "Kỷ Luật (Thẻ/Lỗi)", 
        "Thị Trường Cược",
        "Dữ Liệu Thô"
    ])
    
    # --- TAB 1: TỔNG QUAN & KẾT QUẢ ---
    with tab1:
        st.subheader("Phân Bố Kết Quả Trận Đấu")
        if 'ftr' in df.columns:
            ftr_counts = df['ftr'].value_counts().reset_index()
            ftr_counts.columns = ['Result', 'Count']
            # Map mã kết quả sang tên hiển thị
            ftr_counts['Result Name'] = ftr_counts['Result'].map({'H': 'Đội Nhà Thắng', 'A': 'Đội Khách Thắng', 'D': 'Hòa'})
            
            fig_pie = px.pie(ftr_counts, values='Count', names='Result Name', 
                         color='Result Name',
                         color_discrete_map={'Đội Nhà Thắng':'#1f77b4', 'Đội Khách Thắng':'#ff7f0e', 'Hòa':'#2ca02c'})
            st.plotly_chart(fig_pie, use_container_width=True)

    # --- TAB 2: THỐNG KÊ TẤN CÔNG ---
    with tab2:
        st.subheader("Hoạt Động Sút Bóng Theo Ngày")
        if 'date' in df.columns:
            daily_shots = df.groupby('date')[['hs', 'as', 'hst', 'ast']].sum().reset_index()
            fig_shots = go.Figure()
            fig_shots.add_trace(go.Scatter(x=daily_shots['date'], y=daily_shots['hs'], mode='lines', name='Sút Đội Nhà'))
            fig_shots.add_trace(go.Scatter(x=daily_shots['date'], y=daily_shots['as'], mode='lines', name='Sút Đội Khách'))
            fig_shots.add_trace(go.Scatter(x=daily_shots['date'], y=daily_shots['hst'], mode='lines', name='Sút Trúng Đích (Nhà)', line=dict(dash='dot')))
            fig_shots.add_trace(go.Scatter(x=daily_shots['date'], y=daily_shots['ast'], mode='lines', name='Sút Trúng Đích (Khách)', line=dict(dash='dot')))
            fig_shots.update_layout(xaxis_title='Ngày', yaxis_title='Số Lượng', hovermode="x unified")
            st.plotly_chart(fig_shots, use_container_width=True)

        st.divider()
        
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.subheader("Trung Bình Bàn Thắng")
            avg_goals = df[['fthg', 'ftag']].mean().reset_index()
            avg_goals.columns = ['Type', 'Average']
            avg_goals['Type'] = avg_goals['Type'].replace({'fthg': 'Bàn Thắng Nhà', 'ftag': 'Bàn Thắng Khách'})
            fig_goals = px.bar(avg_goals, x='Type', y='Average', color='Type', text_auto='.2f')
            st.plotly_chart(fig_goals, use_container_width=True)
            
        with col_c2:
            st.subheader("Trung Bình Phạt Góc")
            if 'hc' in df.columns and 'ac' in df.columns:
                avg_corners = df[['hc', 'ac']].mean().reset_index()
                avg_corners.columns = ['Type', 'Average']
                avg_corners['Type'] = avg_corners['Type'].replace({'hc': 'Phạt Góc Nhà', 'ac': 'Phạt Góc Khách'})
                fig_corners = px.bar(avg_corners, x='Type', y='Average', color='Type', text_auto='.2f',
                                     color_discrete_sequence=['#9467bd', '#8c564b'])
                st.plotly_chart(fig_corners, use_container_width=True)

    # --- TAB 3: KỶ LUẬT ---
    with tab3:
        st.subheader("Tương Quan Lỗi & Thẻ Vàng")
        if 'hy' in df.columns and 'hf' in df.columns and 'af' in df.columns:
            fouls_by_hy = df.groupby('hy')[['hf', 'af']].mean().reset_index()
            fouls_melted = fouls_by_hy.melt(id_vars=['hy'], value_vars=['hf', 'af'], 
                                            var_name='Loại Lỗi', value_name='Trung Bình Lỗi')
            fig_fouls = px.bar(fouls_melted, x='hy', y='Trung Bình Lỗi', color='Loại Lỗi', barmode='group',
                         labels={'hy': 'Số Thẻ Vàng Đội Nhà', 'Trung Bình Lỗi': 'Số Lỗi Trung Bình'})
            st.plotly_chart(fig_fouls, use_container_width=True)
            
        st.divider()
        st.subheader("Phân Tích Thẻ Đỏ")
        if 'hr' in df.columns and 'ar' in df.columns:
            total_reds = df[['hr', 'ar']].sum().reset_index()
            total_reds.columns = ['Type', 'Total Count']
            total_reds['Type'] = total_reds['Type'].replace({'hr': 'Thẻ Đỏ Đội Nhà', 'ar': 'Thẻ Đỏ Đội Khách'})
            fig_reds = px.pie(total_reds, values='Total Count', names='Type', 
                              title="Tổng Số Thẻ Đỏ", hole=0.4,
                              color_discrete_sequence=['#d62728', '#ff9896'])
            st.plotly_chart(fig_reds, use_container_width=True)

    # --- TAB 4: THỊ TRƯỜNG CƯỢC ---
    with tab4:
        st.subheader("Xu Hướng Tỷ Lệ Cược (Pinnacle)")
        st.markdown("Tỷ lệ cược trung bình hàng ngày cho: Đội Nhà Thắng (PSH), Hòa (PSD), Đội Khách Thắng (PSA).")
        
        if 'psh' in df.columns and 'date' in df.columns:
            # Lọc bỏ giá trị 0
            odds_df = df[(df['psh'] > 0) & (df['psd'] > 0) & (df['psa'] > 0)]
            
            if not odds_df.empty:
                daily_odds = odds_df.groupby('date')[['psh', 'psd', 'psa']].mean().reset_index()
                
                fig_odds = go.Figure()
                fig_odds.add_trace(go.Scatter(x=daily_odds['date'], y=daily_odds['psh'], name='Cược Nhà Thắng (PSH)'))
                fig_odds.add_trace(go.Scatter(x=daily_odds['date'], y=daily_odds['psd'], name='Cược Hòa (PSD)'))
                fig_odds.add_trace(go.Scatter(x=daily_odds['date'], y=daily_odds['psa'], name='Cược Khách Thắng (PSA)'))
                
                fig_odds.update_layout(xaxis_title='Ngày', yaxis_title='Tỷ Lệ Trung Bình', hovermode="x unified")
                st.plotly_chart(fig_odds, use_container_width=True)
            else:
                st.info("Không có dữ liệu tỷ lệ cược để hiển thị.")
        else:
            st.error("Không tìm thấy cột dữ liệu cược (PSH, PSD, PSA).")

    # --- TAB 5: DỮ LIỆU THÔ ---
    with tab5:
        st.header("Dữ Liệu Thô")
        
        # Hiển thị tổng số bản ghi
        total_in_es = df.attrs.get('total_in_es', len(df))
        fetched = len(df)
        
        if total_in_es > fetched:
            st.info(f"📊 **Tổng bản ghi trong Elasticsearch:** {total_in_es:,} | **Đang hiển thị:** {fetched:,} (Giới hạn query)")
            st.caption("💡 Lưu ý: Elasticsearch mặc định giới hạn 10,000 bản ghi mỗi query. Dữ liệu vẫn được lưu đầy đủ, nhưng chỉ hiển thị 10,000 bản ghi mới nhất tại đây.")
        else:
            st.write(f"**Tổng bản ghi:** {len(df):,}")
        
        # Phân trang
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            page_size = st.selectbox("Số dòng mỗi trang", [50, 100, 200, 500, 1000], index=1)
        with col2:
            total_pages = (len(df) - 1) // page_size + 1
            page_number = st.number_input(f"Trang (1-{total_pages})", min_value=1, max_value=total_pages, value=1)
        
        # Tính chỉ số bắt đầu và kết thúc
        start_idx = (page_number - 1) * page_size
        end_idx = min(start_idx + page_size, len(df))
        
        # Hiển thị bảng dữ liệu
        st.write(f"Hiển thị bản ghi {start_idx + 1} đến {end_idx} trong tổng số {len(df):,}")
        st.dataframe(df.iloc[start_idx:end_idx], use_container_width=True, height=600)
    
    # Logic tự động làm mới
    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()

if __name__ == '__main__':
    main()
