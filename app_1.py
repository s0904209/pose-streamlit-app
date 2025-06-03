import streamlit as st
import cv2
import mediapipe as mp
import tempfile
import os

st.title("📹 MediaPipe Pose Detection with Streamlit")

# 檔案上傳區塊
video_file = st.file_uploader("上傳影片檔案", type=["mp4", "avi", "mov"])

if video_file:
    # 將影片寫入暫存檔
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(video_file.read())
    video_path = tfile.name

    st.video(video_file)  # 顯示原始影片

    st.markdown("### 🔍 處理中...")
    mp_drawing = mp.solutions.drawing_utils
    mp_pose = mp.solutions.pose

    cap = cv2.VideoCapture(video_path)

    stframe = st.empty()
    pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(frame)

        if results.pose_landmarks:
            mp_drawing.draw_landmarks(
                frame,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS
            )

        frame = cv2.resize(frame, (640, 480))
        stframe.image(frame, channels="RGB")

    cap.release()
    os.unlink(video_path)
    st.success("✅ 處理完成！")

