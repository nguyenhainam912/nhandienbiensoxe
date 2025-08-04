import streamlit as st
import cv2
import numpy as np
import math
import Preprocess
import os
import requests
from PIL import Image

st.set_page_config(layout="wide")
st.title("Nhận diện biển số xe theo thời gian thực")

# API endpoints
DATABASE_API_SAVE = "http://localhost:8001/save_license_plate"
DATABASE_API_EXIT = "http://localhost:8001/update_exit"

# Configuration
ADAPTIVE_THRESH_BLOCK_SIZE = 19
ADAPTIVE_THRESH_WEIGHT = 9
Min_char_area = 0.015
Max_char_area = 0.06
Min_char = 0.01
Max_char = 0.09
Min_ratio_char = 0.25
Max_ratio_char = 0.7
RESIZED_IMAGE_WIDTH = 20
RESIZED_IMAGE_HEIGHT = 30

base_dir = os.path.dirname(__file__)
class_path = os.path.join(base_dir, "classifications.txt")
class_path1 = os.path.join(base_dir, "flattened_images.txt")

# Load KNN
npaClassifications = np.loadtxt(class_path, np.float32)
npaFlattenedImages = np.loadtxt(class_path1, np.float32)
npaClassifications = npaClassifications.reshape((npaClassifications.size, 1))
kNearest = cv2.ml.KNearest_create()
kNearest.train(npaFlattenedImages, cv2.ml.ROW_SAMPLE, npaClassifications)

# OpenCV camera
cap = cv2.VideoCapture(0)

# Two-column layout for video
col1, col2 = st.columns(2)
frame_placeholder1 = col1.empty()
frame_placeholder2 = col2.empty()

tongframe = 0
biensotimthay = 0

che_do = st.radio("Chọn chế độ ghi nhận", ["Vào", "Ra"], horizontal=True)

if "camera_on" not in st.session_state:
    st.session_state.camera_on = False

# Start/Stop camera button
if st.button("Bật / Tắt Video"):
    st.session_state.camera_on = not st.session_state.camera_on

while cap.isOpened():
    if not st.session_state.camera_on:
        st.info("Video đang tắt. Nhấn nút 'Bật / Tắt Video' để bắt đầu.")
        st.stop()

    ret, img = cap.read()
    if not ret:
        st.warning("Không thể đọc từ camera.")
        break

    tongframe += 1
    raw_img = img.copy()

    strFinalString = ""
    imgGrayscaleplate, imgThreshplate = Preprocess.preprocess(img)
    canny_image = cv2.Canny(imgThreshplate, 250, 255)
    kernel = np.ones((3, 3), np.uint8)
    dilated_image = cv2.dilate(canny_image, kernel, iterations=1)

    contours, _ = cv2.findContours(dilated_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]
    screenCnts = []

    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.06 * peri, True)
        [x, y, w, h] = cv2.boundingRect(approx.copy())
        ratio = w / h
        if (len(approx) == 4) and (0.8 <= ratio <= 1.5 or 4.5 <= ratio <= 6.5):
            screenCnts.append(approx)

    for screenCnt in screenCnts:
        (x1, y1) = screenCnt[0, 0]
        (x2, y2) = screenCnt[1, 0]
        (x3, y3) = screenCnt[2, 0]
        (x4, y4) = screenCnt[3, 0]
        array = [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
        array.sort(reverse=True, key=lambda x: x[1])
        (x1, y1) = array[0]
        (x2, y2) = array[1]

        doi = abs(y1 - y2)
        ke = abs(x1 - x2)
        angle = math.atan(doi / ke) * (180.0 / math.pi)

        mask = np.zeros(imgGrayscaleplate.shape, np.uint8)
        cv2.drawContours(mask, [screenCnt], 0, 255, -1)
        (x, y) = np.where(mask == 255)
        if len(x) == 0 or len(y) == 0:
            continue
        (topx, topy) = (np.min(x), np.min(y))
        (bottomx, bottomy) = (np.max(x), np.max(y))

        roi = img[topx:bottomx + 1, topy:bottomy + 1]
        imgThresh = imgThreshplate[topx:bottomx + 1, topy:bottomy + 1]
        ptPlateCenter = (bottomx - topx) / 2, (bottomy - topy) / 2

        if x1 < x2:
            rotationMatrix = cv2.getRotationMatrix2D(ptPlateCenter, -angle, 1.0)
        else:
            rotationMatrix = cv2.getRotationMatrix2D(ptPlateCenter, angle, 1.0)

        roi = cv2.warpAffine(roi, rotationMatrix, (bottomy - topy, bottomx - topx))
        imgThresh = cv2.warpAffine(imgThresh, rotationMatrix, (bottomy - topy, bottomx - topx))

        roi = cv2.resize(roi, (0, 0), fx=3, fy=3)
        imgThresh = cv2.resize(imgThresh, (0, 0), fx=3, fy=3)

        kernel3 = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        thre_mor = cv2.morphologyEx(imgThresh, cv2.MORPH_DILATE, kernel3)
        cont, _ = cv2.findContours(thre_mor, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        char_x_ind = {}
        char_x = []
        height, width, _ = roi.shape
        roiarea = height * width

        for ind, cnt in enumerate(cont):
            area = cv2.contourArea(cnt)
            (x, y, w, h) = cv2.boundingRect(cnt)
            ratiochar = w / h
            if (Min_char * roiarea < area < Max_char * roiarea) and (0.25 < ratiochar < 0.7):
                if x in char_x:
                    x += 1
                char_x.append(x)
                char_x_ind[x] = ind

        if len(char_x) in range(7, 10):
            cv2.drawContours(img, [screenCnt], -1, (0, 255, 0), 3)
            char_x.sort()
            first_line = ""
            second_line = ""
            for i in char_x:
                (x, y, w, h) = cv2.boundingRect(cont[char_x_ind[i]])
                imgROI = thre_mor[y:y + h, x:x + w]
                imgROIResized = cv2.resize(imgROI, (RESIZED_IMAGE_WIDTH, RESIZED_IMAGE_HEIGHT))
                npaROIResized = imgROIResized.reshape((1, RESIZED_IMAGE_WIDTH * RESIZED_IMAGE_HEIGHT)).astype(np.float32)

                _, npaResults, _, _ = kNearest.findNearest(npaROIResized, k=3)
                strCurrentChar = str(chr(int(npaResults[0][0])))
                if y < height / 3:
                    first_line += strCurrentChar
                else:
                    second_line += strCurrentChar

            strFinalString = first_line + second_line
            cv2.putText(img, strFinalString, (topy, topx), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
            biensotimthay += 1

    # Display videos
    raw_img_resized = cv2.resize(raw_img, (640, 480))
    processed_img_resized = cv2.resize(img, (640, 480))
    frame_placeholder1.image(raw_img_resized, caption="Video gốc", channels="BGR")
    frame_placeholder2.image(processed_img_resized, caption="Video đã xử lý", channels="BGR")

    # Call Database Service APIs
    if tongframe % 10 == 0 and strFinalString and len(strFinalString) in [8, 9]:
        try:
            if che_do == "Vào":
                response = requests.post(DATABASE_API_SAVE, json={"bien_so": strFinalString, "frame_count": tongframe})
                if response.status_code == 200:
                    result = response.json()
                    if result["status"] == "Vào":
                        st.toast(f"✅ Xe: {result['bien_so']} đã vào bãi gửi.", icon="🚗")
            else:
                response = requests.post(DATABASE_API_EXIT, json={"bien_so": strFinalString})
                if response.status_code == 200:
                    result = response.json()
                    if "tong_tien" in result:
                        st.toast(f"""🚙 Xe {result['bien_so']} đã rời bãi.
                        💰 Phí gửi: {result['tong_tien']:,} VND""")
        except requests.RequestException as e:
            st.error(f"Lỗi khi gọi API: {e}")

cap.release()