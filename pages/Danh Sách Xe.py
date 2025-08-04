import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# Cấu hình giao diện
st.set_page_config(
    page_title="Xem Dữ Liệu Biển Số",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS với màu sắc phù hợp theme tối
st.markdown("""
    <style>
    /* Main container styling */
    .main {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    
    /* Header styling */
    .header-container {
        background-color: #262730;
        padding: 1rem 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    /* Filter section styling */
    .filter-section {
        background-color: #262730;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
    }
    
    /* Data table styling */
    div[data-testid="stDataFrame"] {
        background-color: #262730;
        color: #FAFAFA;
    }
    
    /* Input fields styling */
    .stTextInput > div > div > input {
        background-color: #0E1117;
        color: #FAFAFA;
        border: 1px solid #555;
    }
    
    .stSelectbox > div > div {
        background-color: #0E1117;
        color: #FAFAFA;
        border: 1px solid #555;
    }
    
    /* Results count styling */
    .results-count {
        background-color: #1E1E1E;
        color: #FAFAFA;
        padding: 0.8rem 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid #00ADB5;
    }
    
    /* Text colors */
    h1, h2, h3, p, label {
        color: #FAFAFA !important;
    }
    
    .stMarkdown {
        color: #FAFAFA;
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
    
    /* Status badge styling */
    .status-in {
        background-color: #00ADB5;
        color: #FAFAFA;
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 0.9em;
    }
    
    .status-out {
        background-color: #393E46;
        color: #FAFAFA;
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 0.9em;
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
        <h2>🚘 Danh Sách Biển Số Xe</h2>
    </div>
""", unsafe_allow_html=True)

# API endpoint
DATABASE_API_GET = "http://localhost:8001/get_license_plates"

# Khu vực filter
st.markdown('<div class="filter-section">', unsafe_allow_html=True)
col1, col2, col3 = st.columns([2, 2, 3])

with col1:
    trang_thai = st.selectbox(
        "↕️ Trạng thái:",
        ["Tất cả", "Vào", "Ra"],
        help="Lọc danh sách theo trạng thái xe ra/vào"
    )

with col2:
    sort_by = st.selectbox(
        "🔃 Sắp xếp:",
        ["Thời gian vào", "Biển số", "Trạng thái"],
        help="Chọn tiêu chí sắp xếp danh sách"
    )

with col3:
    search = st.text_input(
        "🔍 Tìm kiếm:",
        placeholder="Nhập biển số xe...",
        help="Tìm kiếm theo biển số xe"
    )
st.markdown('</div>', unsafe_allow_html=True)

# Xử lý dữ liệu
try:
    params = {"trang_thai": trang_thai} if trang_thai != "Tất cả" else {}
    response = requests.get(DATABASE_API_GET, params=params)
    response.raise_for_status()
    records = response.json()

    if records:
        df = pd.DataFrame(records)
        
        # Xử lý tìm kiếm
        if search:
            df = df[df['bien_so'].str.contains(search, case=False, na=False)]
        
        # Xử lý sắp xếp
        sort_column = {
            "Thời gian vào": "thoi_gian_vao",
            "Biển số": "bien_so",
            "Trạng thái": "trang_thai"
        }[sort_by]
        df = df.sort_values(by=sort_column, ascending=False)
        
        # Định dạng thời gian
        for col in ['thoi_gian_vao', 'thoi_gian_ra']:
            if col in df:
                df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%H:%M:%S %d-%m-%Y')
        
        # Đổi tên cột
        column_mapping = {
            'bien_so': 'Biển số xe',
            'trang_thai': 'Trạng thái',
            'thoi_gian_vao': 'Thời gian vào',
            'thoi_gian_ra': 'Thời gian ra',
            'tong_tien': 'Phí gửi xe'
        }
        df = df.rename(columns=column_mapping)
        
        # Hiển thị số lượng kết quả
        st.markdown(f"""
            <div class="results-count">
                <h3 style='margin:0; font-size:1.1em;'>📊 Tổng số: {len(df)} xe</h3>
            </div>
        """, unsafe_allow_html=True)
        
        # Hiển thị bảng dữ liệu
        st.dataframe(
            df,
            use_container_width=True,
            height=500,
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
        st.info("🔍 Không tìm thấy dữ liệu.")

except requests.RequestException as e:
    st.error(f"❌ Lỗi kết nối: {str(e)}")

# Footer
st.markdown("""
    <div class="footer">
        <p style='margin:0;'>© 2024 Hệ Thống Quản Lý Bãi Đỗ Xe</p>
    </div>
""", unsafe_allow_html=True)