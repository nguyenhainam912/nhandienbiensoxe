import streamlit as st
import pandas as pd
import requests

# Cấu hình giao diện
st.set_page_config(page_title="Xem Dữ Liệu Biển Số", page_icon="🚗", layout="wide")
st.title("🚘 Danh sách biển số xe")

# API endpoint
DATABASE_API_GET = "http://localhost:8001/get_license_plates"

# Bộ lọc trạng thái
trang_thai = st.selectbox("Chọn trạng thái xe:", ["Tất cả", "Vào", "Ra"])

# Lấy dữ liệu từ Database Service
try:
    params = {"trang_thai": trang_thai} if trang_thai != "Tất cả" else {}
    response = requests.get(DATABASE_API_GET, params=params)
    response.raise_for_status()  # Raise an exception for bad status codes
    records = response.json()

    # Hiển thị dữ liệu
    if records:
        df = pd.DataFrame(records)
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("Không có dữ liệu phù hợp.")
except requests.RequestException as e:
    st.error(f"Lỗi khi gọi API: {e}")