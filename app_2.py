import streamlit as st
import cv2
import tempfile
import json
from datetime import datetime
import mediapipe as mp

st.title("🎯 MediaPipe 姿勢偵測 + JSON 匯出")
uploaded_file = st.file_uploader("請上傳影片", type=["mp4", "mov", "avi"])

if uploaded_file:
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(uploaded_file.read())

    cap = cv2.VideoCapture(tfile.name)

    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(static_image_mode=False)
    results_list = []

    stframe = st.empty()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image_rgb)

        if results.pose_landmarks:
            frame_data = {
                "timestamp": datetime.now().isoformat(),
                "landmarks": [
                    {
                        "x": lm.x,
                        "y": lm.y,
                        "z": lm.z,
                        "visibility": lm.visibility
                    } for lm in results.pose_landmarks.landmark
                ]
            }
            results_list.append(frame_data)

        # 顯示
        annotated = frame.copy()
        mp.solutions.drawing_utils.draw_landmarks(
            annotated, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        stframe.image(annotated, channels="BGR")

    cap.release()

    # JSON 匯出按鈕
    if results_list:
        json_data = json.dumps(results_list, indent=2)
        st.download_button("⬇️ 下載姿勢資料 JSON", json_data, file_name="pose_data.json")

