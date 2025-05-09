# view_data.py
import streamlit as st
import pandas as pd
from db import get_bien_so_by_trang_thai

# Cấu hình giao diện
st.set_page_config(page_title="Xem Dữ Liệu Biển Số", page_icon="🚗", layout="wide")
st.title("🚘 Danh sách biển số xe")

# Bộ lọc trạng thái
trang_thai = st.selectbox("Chọn trạng thái xe:", ["Tất cả", "Vào", "Ra"])

# Lấy dữ liệu từ database
records = get_bien_so_by_trang_thai(trang_thai)

# Hiển thị
if records:
    df = pd.DataFrame(records)
    st.dataframe(df, use_container_width=True)
else:
    st.warning("Không có dữ liệu phù hợp.")
