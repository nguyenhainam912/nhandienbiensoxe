# app.py
import streamlit as st

# Cấu hình trang
st.set_page_config(
    page_title="Hệ Thống Quản Lý Bãi Đỗ Xe",
    page_icon="🚗",
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
    
    /* Header styling */
    .header-container {
        background-color: #262730;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    /* Feature card styling */
    .feature-container {
        display: flex;
        justify-content: space-between;
        margin: 2rem 0;
        gap: 1rem;
    }
    
    .feature-card {
        background-color: #262730;
        padding: 1.5rem;
        border-radius: 10px;
        flex: 1;
        text-align: center;
        transition: transform 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
    }
    
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    
    /* Text colors */
    h1, h2, h3, p {
        color: #FAFAFA !important;
    }
    
    /* Footer styling */
    .footer {
        text-align: center;
        padding: 2rem;
        color: #FAFAFA;
        background-color: #262730;
        border-radius: 10px;
        margin-top: 2rem;
    }
    
    /* Welcome section */
    .welcome-text {
        text-align: center;
        margin: 2rem 0;
        padding: 2rem;
        background-color: #262730;
        border-radius: 10px;
    }
    
    /* Stats section */
    .stats-container {
        background-color: #262730;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 2rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
    <div class="header-container">
        <h1 style='font-size: 2.5em; margin-bottom: 0.5rem;'>🚗 Hệ Thống Quản Lý Bãi Đỗ Xe Thông Minh</h1>
        <p style='font-size: 1.2em; opacity: 0.9;'>Giải pháp quản lý hiện đại với công nghệ nhận diện biển số</p>
    </div>
""", unsafe_allow_html=True)

# Welcome section
st.markdown("""
    <div class="welcome-text">
        <h2 style='margin-bottom: 1rem;'>👋 Chào mừng bạn!</h2>
        <p style='font-size: 1.1em; line-height: 1.6;'>
            Hệ thống của chúng tôi cung cấp giải pháp toàn diện cho việc quản lý bãi đỗ xe,
            tích hợp công nghệ nhận diện biển số tự động và theo dõi thời gian thực.
        </p>
    </div>
""", unsafe_allow_html=True)

# Feature cards
st.markdown("""
    <div class="feature-container">
        <div class="feature-card">
            <div class="feature-icon">🎯</div>
            <h3>Nhận Diện Chính Xác</h3>
            <p>Công nghệ AI hiện đại giúp nhận diện biển số xe với độ chính xác cao</p>
        </div>
        <div class="feature-card">
            <div class="feature-icon">⚡</div>
            <h3>Xử Lý Nhanh Chóng</h3>
            <p>Thời gian xử lý nhanh, đảm bảo không ùn tắc tại cổng ra/vào</p>
        </div>
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <h3>Thống Kê Chi Tiết</h3>
            <p>Báo cáo và thống kê đầy đủ, hỗ trợ ra quyết định quản lý</p>
        </div>
    </div>
""", unsafe_allow_html=True)

# Quick stats
st.markdown("""
    <div class="stats-container">
        <h2 style='text-align: center; margin-bottom: 1.5rem;'>📈 Tính Năng Nổi Bật</h2>
        <div style='display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; text-align: center;'>
            <div>
                <h3 style='color: #00ADB5;'>Quản Lý Xe</h3>
                <p>Theo dõi xe ra/vào thời gian thực</p>
            </div>
            <div>
                <h3 style='color: #00ADB5;'>Tính Phí Tự Động</h3>
                <p>Tính toán phí gửi xe chính xác</p>
            </div>
            <div>
                <h3 style='color: #00ADB5;'>Báo Cáo Thống Kê</h3>
                <p>Xem báo cáo chi tiết theo thời gian</p>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Hướng dẫn sử dụng
st.markdown("""
    <div style='background-color: #262730; padding: 1.5rem; border-radius: 10px; margin: 2rem 0;'>
        <h2 style='text-align: center; margin-bottom: 1rem;'>🎓 Hướng Dẫn Sử Dụng</h2>
        <div style='display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem;'>
            <div>
                <h3 style='color: #00ADB5;'>1. Xem Thống Kê</h3>
                <p>Truy cập trang Dashboard để xem thống kê tổng quan về hoạt động bãi xe</p>
            </div>
            <div>
                <h3 style='color: #00ADB5;'>2. Quản Lý Xe</h3>
                <p>Sử dụng trang Danh Sách để xem và tìm kiếm thông tin các xe</p>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Footer
st.markdown("""
    <div class="footer">
        <p style='margin-bottom: 0.5rem;'>© 2024 Hệ Thống Quản Lý Bãi Đỗ Xe</p>
        <p style='font-size: 0.9em; opacity: 0.8;'>Phát triển bởi Nhóm Sinh Viên</p>
    </div>
""", unsafe_allow_html=True)

