import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime

# Cấu hình giao diện
st.set_page_config(
    page_title="Thống Kê Biển Số Xe",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS với theme tối
st.markdown("""
    <style>
    /* Main container styling */
    .main {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    
    /* Metric styling */
    .stMetric {
        background-color: #262730;
        padding: 1rem;
        border-radius: 10px;
        color: #FAFAFA;
    }
    
    .stMetric:hover {
        transform: translateY(-2px);
        transition: all 0.3s ease;
    }
    
    /* Data table styling */
    div[data-testid="stDataFrame"] {
        background-color: #262730;
        padding: 1rem;
        border-radius: 10px;
        color: #FAFAFA;
    }
    
    /* Header styling */
    .header-container {
        background-color: #262730;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: #FAFAFA;
    }
    
    /* Text colors */
    h1, h2, h3, p, label {
        color: #FAFAFA !important;
    }
    
    .metric-container {
        background-color: #262730;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
    }
    
    /* Chart styling */
    .stPlotlyChart {
        background-color: #262730;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    
    /* Footer styling */
    .footer {
        text-align: center;
        padding: 1.5rem;
        color: #FAFAFA;
        background-color: #262730;
        border-radius: 10px;
        margin-top: 2rem;
    }
    
    /* Help text color */
    .stMarkdown div[data-testid="stMarkdownContainer"] {
        color: #FAFAFA;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
    <div class="header-container">
        <h2 style='margin-bottom: 0.5rem;'>📊 Dashboard Thống Kê</h2>
        <p style='font-size: 1.1em; opacity: 0.9; margin: 0;'>Hệ thống quản lý bãi đỗ xe thông minh</p>
    </div>
""", unsafe_allow_html=True)

# API endpoint
DATABASE_API_GET = "http://localhost:8001/get_license_plates"

# Hàm lấy dữ liệu từ Database Service
@st.cache_data(ttl=60)
def fetch_data(trang_thai=None):
    try:
        params = {"trang_thai": trang_thai} if trang_thai and trang_thai != "Tất cả" else {}
        response = requests.get(DATABASE_API_GET, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"❌ Lỗi kết nối: {str(e)}")
        return []

# Lấy dữ liệu
all_records = fetch_data()

if all_records:
    df = pd.DataFrame(all_records)
    
    # Tính toán thống kê
    total_vehicles = len(df)
    vehicles_in = len(df[df["trang_thai"] == "Vào"])
    vehicles_out = len(df[df["trang_thai"] == "Ra"])
    total_revenue = df[df["trang_thai"] == "Ra"]["tong_tien"].sum() if "tong_tien" in df else 0
    
    # Container cho các metric
    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "🚗 Tổng số xe",
            f"{total_vehicles:,}",
            help="Tổng số xe đã ghi nhận"
        )
    with col2:
        st.metric(
            "⬆️ Xe trong bãi",
            f"{vehicles_in:,}",
            delta=f"{vehicles_in/total_vehicles*100:.1f}%" if total_vehicles > 0 else "0%",
            help="Số xe hiện đang trong bãi"
        )
    with col3:
        st.metric(
            "⬇️ Xe đã ra",
            f"{vehicles_out:,}",
            delta=f"{vehicles_out/total_vehicles*100:.1f}%" if total_vehicles > 0 else "0%",
            help="Số xe đã rời bãi"
        )
    with col4:
        st.metric(
            "💰 Doanh thu",
            f"{total_revenue:,.0f}₫",
            help="Tổng doanh thu từ phí gửi xe"
        )
    st.markdown('</div>', unsafe_allow_html=True)

    # Biểu đồ phân tích
    st.markdown("### 📊 Phân Tích Dữ Liệu")
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        status_counts = df["trang_thai"].value_counts().reset_index()
        status_counts.columns = ["Trạng thái", "Số lượng"]
        fig1 = px.bar(
            status_counts,
            x="Trạng thái",
            y="Số lượng",
            title="Số lượng xe theo trạng thái",
            color="Trạng thái",
            color_discrete_map={"Vào": "#00ADB5", "Ra": "#393E46"}
        )
        fig1.update_layout(
            plot_bgcolor="#262730",
            paper_bgcolor="#262730",
            font=dict(color="#FAFAFA", size=12),
            title_font_color="#FAFAFA",
            xaxis=dict(gridcolor="#3b3b3b"),
            yaxis=dict(gridcolor="#3b3b3b")
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with chart_col2:
        df["hour"] = pd.to_datetime(df["thoi_gian_vao"]).dt.hour
        hourly_dist = df["hour"].value_counts().sort_index()
        fig2 = px.line(
            x=hourly_dist.index,
            y=hourly_dist.values,
            title="Phân bố xe theo giờ",
            labels={"x": "Giờ trong ngày", "y": "Số lượng xe"}
        )
        fig2.update_layout(
            plot_bgcolor="#262730",
            paper_bgcolor="#262730",
            font=dict(color="#FAFAFA", size=12),
            title_font_color="#FAFAFA",
            xaxis=dict(gridcolor="#3b3b3b"),
            yaxis=dict(gridcolor="#3b3b3b")
        )
        fig2.update_traces(line_color="#00ADB5")
        st.plotly_chart(fig2, use_container_width=True)
    
    # Bảng dữ liệu gần đây
    st.markdown("### 📋 Giao Dịch Gần Đây")
    recent_records = df.sort_values(by="thoi_gian_vao", ascending=False).head(10)
    
    # Định dạng thời gian
    for col in ['thoi_gian_vao', 'thoi_gian_ra']:
        if col in recent_records:
            recent_records[col] = pd.to_datetime(recent_records[col], errors='coerce').dt.strftime('%H:%M:%S %d-%m-%Y')
    
    # Định dạng DataFrame
    display_df = recent_records[["bien_so", "trang_thai", "thoi_gian_vao", "thoi_gian_ra", "tong_tien"]].copy()
    display_df.columns = ["Biển số xe", "Trạng thái", "Thời gian vào", "Thời gian ra", "Phí gửi xe"]
    
    st.dataframe(
        display_df,
        use_container_width=True,
        height=400,
        column_config={
            "Biển số xe": st.column_config.TextColumn(
                help="Biển số xe",
                width="medium",
            ),
            "Trạng thái": st.column_config.TextColumn(
                help="Trạng thái xe ra/vào bãi",
                width="small",
            ),
            "Phí gửi xe": st.column_config.NumberColumn(
                help="Phí gửi xe (VNĐ)",
                format="%d ₫",
                width="medium",
            ),
        },
        hide_index=True,
    )

else:
    st.info("🔍 Không có dữ liệu để hiển thị")

# Footer
st.markdown("""
    <div class="footer">
        <p style='margin:0;'>© 2024 Hệ Thống Quản Lý Bãi Đỗ Xe</p>
    </div>
""", unsafe_allow_html=True)