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

def main():
    st.title("🎯 MediaPipe 姿勢偵測 + 儲存至 PostgreSQL")
    uploaded_file = st.file_uploader("請上傳影片", type=["mp4", "mov", "avi"])

    if uploaded_file:
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(uploaded_file.read())

        cap = cv2.VideoCapture(tfile.name)
        mp_pose = mp.solutions.pose
        pose = mp_pose.Pose(static_image_mode=False)
        stframe = st.empty()

        try:
            # 連線資料庫
            conn = psycopg2.connect(
                host="localhost",
                port=5432,
                database="pose_db",
                user="postgres",
                password="1234"
            )
            init_db(conn)

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

        except Exception as e:
            st.error(f"資料庫連線或寫入錯誤：{e}")
        finally:
            cap.release()
            if 'conn' in locals():
                conn.close()

if __name__ == "__main__":
    main()

