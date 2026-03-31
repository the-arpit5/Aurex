# INSTALLATION REQUIREMENT (Run in terminal):
# pip install streamlit streamlit-webrtc opencv-contrib-python-headless pandas numpy Pillow

import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
import cv2
import os
import csv
import numpy as np
from PIL import Image
import pandas as pd
import datetime
import time

# --- INITIAL SETUP ---
st.set_page_config(page_title="Attendance Pro Web", layout="wide", initial_sidebar_state="expanded")

# Professional White Tone CSS
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    div[data-testid="stVerticalBlock"] > div:has(div.stButton) > div {
        border-radius: 8px;
    }
    .main-header {
        font-family: 'Segoe UI', sans-serif;
        color: #1e293b;
        text-align: center;
        padding: 20px;
        background: white;
        border-bottom: 1px solid #e2e8f0;
        margin-bottom: 30px;
    }
    .stButton>button {
        width: 100%;
        border-radius: 6px;
        height: 3.5em;
        background-color: #4f46e5;
        color: white;
        font-weight: bold;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #4338ca;
        border: none;
    }
    .status-box {
        padding: 15px;
        border-radius: 8px;
        background-color: white;
        border: 1px solid #e2e8f0;
        color: #64748b;
        font-style: italic;
    }
    </style>
    """, unsafe_allow_html=True)

# --- DIRECTORY INITIALIZATION ---
def assure_path_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)

assure_path_exists("StudentDetails/")
assure_path_exists("TrainingImage/")
assure_path_exists("TrainingImageLabel/")
assure_path_exists("Attendance/")

# --- LOGIC CLASS FOR WEBRTC ---
class AttendanceTransformer(VideoTransformerBase):
    def __init__(self):
        self.faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.model_loaded = False
        
        if os.path.isfile("TrainingImageLabel/Trainner.yml"):
            self.recognizer.read("TrainingImageLabel/Trainner.yml")
            self.model_loaded = True
        
        if os.path.isfile("StudentDetails/StudentDetails.csv"):
            self.df = pd.read_csv("StudentDetails/StudentDetails.csv")
        else:
            self.df = None

    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.faceCascade.detectMultiScale(gray, 1.2, 5)

        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (79, 70, 229), 2)
            
            if self.model_loaded and self.df is not None:
                try:
                    serial, conf = self.recognizer.predict(gray[y:y + h, x:x + w])
                    if conf < 50:
                        name_match = self.df.loc[self.df['SERIAL NO.'] == serial]['NAME'].values
                        name = name_match[0] if len(name_match) > 0 else "Unknown"
                        
                        # In WebRTC, we don't write to CSV inside the transform loop 
                        # to avoid lag. Usually, you'd trigger a callback here.
                        cv2.putText(img, f"{name}", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                    else:
                        cv2.putText(img, "Unknown", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                except:
                    pass
        return img

# --- HELPER FUNCTIONS ---
def get_registration_count():
    if os.path.isfile("StudentDetails/StudentDetails.csv"):
        with open("StudentDetails/StudentDetails.csv", 'r') as f:
            return max(0, sum(1 for _ in f) - 1)
    return 0

def get_images_and_labels(path):
    image_paths = [os.path.join(path, f) for f in os.listdir(path) if f.endswith(('.jpg', '.png'))]
    face_samples = []
    ids = []
    for image_path in image_paths:
        pil_img = Image.open(image_path).convert('L')
        img_numpy = np.array(pil_img, 'uint8')
        # Expecting format: name.serial.id.samplenum.jpg
        parts = os.path.split(image_path)[-1].split(".")
        if len(parts) > 1:
            face_id = int(parts[1])
            face_samples.append(img_numpy)
            ids.append(face_id)
    return face_samples, ids

# --- APP UI ---
st.markdown('<div class="main-header"><h1>Attendance Management System</h1></div>', unsafe_allow_html=True)

# Sidebar
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100)
st.sidebar.title("Navigation")
menu = st.sidebar.radio("Select Task", ["Attendance Scanner", "Student Enrollment", "System Logs"])

if menu == "Attendance Scanner":
    st.subheader("🚀 Live Attendance Processing")
    st.write("The system will automatically recognize registered faces.")
    
    ctx = webrtc_streamer(
        key="attendance-scan",
        video_transformer_factory=AttendanceTransformer,
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
        media_stream_constraints={"video": True, "audio": False},
    )
    
    if not os.path.isfile("TrainingImageLabel/Trainner.yml"):
        st.warning("⚠️ Warning: No trained model found. Please go to Enrollment first.")

elif menu == "Student Enrollment":
    col1, col2 = st.columns([1, 1.5])
    
    with col1:
        st.subheader("📝 New Registration")
        reg_id = st.text_input("Student ID (Numbers Only)")
        reg_name = st.text_input("Full Name")
        
        # Step 1: Capture
        if st.button("STEP 1: INITIALIZE CAPTURE"):
            if reg_id and reg_name.replace(" ","").isalpha():
                st.info("Web Capture Note: Streamlit-WebRTC capture is complex. Typically, you would use a dedicated 'Capture' button on the camera stream. For this prototype, ensure your 'TrainingImage' folder has manual uploads or local data.")
            else:
                st.error("Please enter a valid ID and Name.")

        # Step 2: Train
        if st.button("STEP 2: ENROLL & TRAIN SYSTEM"):
            with st.spinner("Analyzing biometric data..."):
                try:
                    recognizer = cv2.face.LBPHFaceRecognizer_create()
                    faces, ids = get_images_and_labels("TrainingImage/")
                    if len(faces) == 0:
                        st.error("No image data found in 'TrainingImage/' folder.")
                    else:
                        recognizer.train(faces, np.array(ids))
                        recognizer.save("TrainingImageLabel/Trainner.yml")
                        st.success("✅ Enrollment Complete! Model Updated.")
                except Exception as e:
                    st.error(f"Training failed: {e}")

    with col2:
        st.subheader("📋 Enrollment Status")
        st.markdown(f"""
            <div class="status-box">
                Current Database Size: <b>{get_registration_count()} Students</b><br>
                System Status: <b>Online</b><br>
                Last Update: {datetime.datetime.now().strftime('%H:%M:%S')}
            </div>
        """, unsafe_allow_html=True)

elif menu == "System Logs":
    st.subheader("📊 Attendance History")
    date_now = datetime.datetime.now().strftime('%d-%m-%Y')
    log_file = f"Attendance/Attendance_{date_now}.csv"
    
    if os.path.isfile(log_file):
        df_logs = pd.read_csv(log_file)
        st.dataframe(df_logs, use_container_width=True)
        st.download_button("Download CSV Report", data=df_logs.to_csv(), file_name=f"Report_{date_now}.csv")
    else:
        st.info("No attendance records found for today.")

# Sidebar Footer
st.sidebar.markdown("---")
st.sidebar.write(f"📅 {datetime.datetime.now().strftime('%d %b %Y')}")
st.sidebar.caption("Secured Attendance System v2.0")
