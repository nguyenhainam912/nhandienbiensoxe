import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime

# Cấu hình giao diện
st.set_page_config(page_title="Thống Kê Biển Số Xe", page_icon="📊", layout="wide")
st.title("📊 Dashboard Thống Kê Biển Số Xe")

# API endpoint
DATABASE_API_GET = "http://localhost:8001/get_license_plates"

# Hàm lấy dữ liệu từ Database Service
@st.cache_data(ttl=60)  # Cache dữ liệu trong 60 giây để cải thiện hiệu suất
def fetch_data(trang_thai=None):
    try:
        params = {"trang_thai": trang_thai} if trang_thai and trang_thai != "Tất cả" else {}
        response = requests.get(DATABASE_API_GET, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Lỗi khi gọi API: {e}")
        return []

# Lấy tất cả dữ liệu
all_records = fetch_data()

# Tính toán thống kê
if all_records:
    df = pd.DataFrame(all_records)
    
    # Tổng số xe
    total_vehicles = len(df)
    vehicles_in = len(df[df["trang_thai"] == "Vào"])
    vehicles_out = len(df[df["trang_thai"] == "Ra"])
    
    # Tổng tiền (chỉ tính cho xe đã ra)
    total_revenue = df[df["trang_thai"] == "Ra"]["tong_tien"].sum() if "tong_tien" in df else 0
    
    # Hiển thị số liệu chính
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Tổng số xe", total_vehicles)
    with col2:
        st.metric("Xe đang trong bãi (Vào)", vehicles_in)
    with col3:
        st.metric("Xe đã rời bãi (Ra)", vehicles_out)
    
    st.metric("Tổng doanh thu", f"{total_revenue:,.0f} VND")
    
    # Biểu đồ số lượng xe theo trạng thái
    status_counts = df["trang_thai"].value_counts().reset_index()
    status_counts.columns = ["Trạng thái", "Số lượng"]
    fig = px.bar(status_counts, x="Trạng thái", y="Số lượng", title="Số lượng xe theo trạng thái",
                 color="Trạng thái", color_discrete_map={"Vào": "blue", "Ra": "green"})
    st.plotly_chart(fig, use_container_width=True)
    
    # Bảng dữ liệu gần đây
    st.subheader("Danh sách giao dịch gần đây")
    recent_records = df.sort_values(by="thoi_gian_vao", ascending=False).head(10)
    if "thoi_gian_vao" in recent_records:
        recent_records["thoi_gian_vao"] = pd.to_datetime(recent_records["thoi_gian_vao"])
        recent_records["thoi_gian_vao"] = recent_records["thoi_gian_vao"].dt.strftime("%Y-%m-%d %H:%M:%S")
    if "thoi_gian_ra" in recent_records:
        recent_records["thoi_gian_ra"] = pd.to_datetime(recent_records["thoi_gian_ra"], errors="coerce")
        recent_records["thoi_gian_ra"] = recent_records["thoi_gian_ra"].dt.strftime("%Y-%m-%d %H:%M:%S")
    st.dataframe(recent_records[["bien_so", "trang_thai", "thoi_gian_vao", "thoi_gian_ra", "tong_tien"]], use_container_width=True)
else:
    st.warning("Không có dữ liệu để hiển thị.")