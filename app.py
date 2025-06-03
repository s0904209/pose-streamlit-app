import streamlit as st
import cv2
import tempfile
import json
from datetime import datetime
import mediapipe as mp
import psycopg2

def init_db(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS pose_data (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP,
                pose_json JSONB
            );
        """)
        conn.commit()

def save_pose_data(conn, timestamp, landmarks_json):
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO pose_data (timestamp, pose_json) VALUES (%s, %s)",
            (timestamp, json.dumps(landmarks_json))
        )
        conn.commit()

def process_video(cap, conn, stframe):
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(static_image_mode=False)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image_rgb)

        if results.pose_landmarks:
            frame_data = {
                "timestamp": datetime.now(),
                "landmarks": [
                    {"x": lm.x, "y": lm.y, "z": lm.z, "visibility": lm.visibility}
                    for lm in results.pose_landmarks.landmark
                ]
            }
            save_pose_data(conn, frame_data["timestamp"], frame_data["landmarks"])

        annotated = frame.copy()
        mp.solutions.drawing_utils.draw_landmarks(
            annotated, results.pose_landmarks, mp_pose.POSE_CONNECTIONS
        )
        stframe.image(annotated, channels="BGR")

    cap.release()

def main():
    st.title("🎯 MediaPipe 姿勢偵測 + 儲存至 PostgreSQL")

    # 連線資料庫
    try:

        conn = psycopg2.connect(
            host="db",        # 重點改這裡，使用 docker-compose 的服務名稱
            port=5432,
            database="pose_db",
            user="postgres",
            password="1234"
        )
        init_db(conn)
    except Exception as e:
        st.error(f"❌ 資料庫連線失敗：{e}")
        return

    # 區塊一：上傳影片
    st.header("📂 上傳影片分析")
    uploaded_file = st.file_uploader("請上傳影片", type=["mp4", "mov", "avi"])

    if uploaded_file:
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(uploaded_file.read())
        cap = cv2.VideoCapture(tfile.name)
        stframe = st.empty()
        process_video(cap, conn, stframe)

    # 區塊二：手機串流
    st.markdown("---")
    st.header("📡 手機直播串流分析")
    stream_url = st.text_input("請輸入手機串流網址 (例如：http://192.168.1.100:8080/video)")

    if stream_url:
        stframe = st.empty()
        cap = cv2.VideoCapture(stream_url)
        if cap.isOpened():
            process_video(cap, conn, stframe)
        else:
            st.error("無法開啟串流，請確認手機 IP 和網路狀態是否正確")

    # 關閉資料庫連線
    conn.close()

if __name__ == "__main__":
    main()
