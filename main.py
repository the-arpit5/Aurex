import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, RTCConfiguration, WebRtcMode
import cv2
import os
import numpy as np
from PIL import Image
import pandas as pd
import datetime
import av # PyAV is required for frame handling

# --- INITIAL SETUP ---
st.set_page_config(page_title="Attendance Pro Web", layout="wide", initial_sidebar_state="expanded")

# Professional White Tone CSS
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
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
    }
    .status-box {
        padding: 15px;
        border-radius: 8px;
        background-color: white;
        border: 1px solid #e2e8f0;
        color: #64748b;
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

# --- MODERN LOGIC CLASS (VideoProcessorBase) ---
class AttendanceProcessor(VideoProcessorBase):
    def __init__(self):
        self.faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.model_loaded = False
        
        # State for capturing
        self.capture_mode = False
        self.capture_count = 0
        self.max_captures = 60
        self.reg_id = ""
        self.reg_name = ""

        if os.path.isfile("TrainingImageLabel/Trainner.yml"):
            try:
                self.recognizer.read("TrainingImageLabel/Trainner.yml")
                self.model_loaded = True
            except:
                self.model_loaded = False
        
        if os.path.isfile("StudentDetails/StudentDetails.csv"):
            self.df = pd.read_csv("StudentDetails/StudentDetails.csv")
        else:
            self.df = None

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.faceCascade.detectMultiScale(gray, 1.2, 5)

        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (79, 70, 229), 2)
            
            # --- CAPTURE LOGIC ---
            if self.capture_mode and self.capture_count < self.max_captures:
                self.capture_count += 1
                # Format: name.id.serial.count.jpg
                img_path = f"TrainingImage/{self.reg_name}.{self.reg_id}.{self.capture_count}.jpg"
                cv2.imwrite(img_path, gray[y:y+h, x:x+w])
                cv2.putText(img, f"Capturing: {self.capture_count}/{self.max_captures}", (x, y-40), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            
            if self.capture_count >= self.max_captures:
                self.capture_mode = False

            # --- RECOGNITION LOGIC ---
            if self.model_loaded and self.df is not None and not self.capture_mode:
                try:
                    serial, conf = self.recognizer.predict(gray[y:y + h, x:x + w])
                    if conf < 50:
                        name_match = self.df.loc[self.df['SERIAL NO.'] == serial]['NAME'].values
                        name = name_match[0] if len(name_match) > 0 else "Unknown"
                        cv2.putText(img, f"{name}", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                    else:
                        cv2.putText(img, "Unknown", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                except:
                    pass
                    
        return av.VideoFrame.from_ndarray(img, format="bgr24")

# --- HELPER FUNCTIONS ---
def get_registration_count():
    if os.path.isfile("StudentDetails/StudentDetails.csv"):
        try:
            df = pd.read_csv("StudentDetails/StudentDetails.csv")
            return len(df)
        except:
            return 0
    return 0

def get_images_and_labels(path):
    image_paths = [os.path.join(path, f) for f in os.listdir(path) if f.endswith(('.jpg', '.png'))]
    face_samples = []
    ids = []
    for image_path in image_paths:
        pil_img = Image.open(image_path).convert('L')
        img_numpy = np.array(pil_img, 'uint8')
        parts = os.path.split(image_path)[-1].split(".")
        if len(parts) > 1:
            try:
                # Based on filename: name.id.count.jpg -> parts[1] is the ID
                face_id = int(parts[1])
                face_samples.append(img_numpy)
                ids.append(face_id)
            except:
                continue
    return face_samples, ids

# --- APP UI ---
st.markdown('<div class="main-header"><h1>Attendance Management System</h1></div>', unsafe_allow_html=True)

st.sidebar.title("Navigation")
menu = st.sidebar.radio("Select Task", ["Attendance Scanner", "Student Enrollment", "System Logs"])

RTC_CONFIG = RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})

if menu == "Attendance Scanner":
    st.subheader("🚀 Live Attendance Processing")
    
    webrtc_streamer(
        key="attendance-scan",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration=RTC_CONFIG,
        video_processor_factory=AttendanceProcessor,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True,
    )
    
    if not os.path.isfile("TrainingImageLabel/Trainner.yml"):
        st.warning("⚠️ Warning: No trained model found. Please go to Enrollment first.")

elif menu == "Student Enrollment":
    col1, col2 = st.columns([1, 1.5])
    
    with col1:
        st.subheader("📝 New Registration")
        reg_id = st.text_input("Student ID (Numbers Only)", placeholder="e.g. 101")
        reg_name = st.text_input("Full Name", placeholder="e.g. John Doe")
        
        # Camera for Enrollment
        ctx = webrtc_streamer(
            key="enrollment-cap",
            mode=WebRtcMode.SENDRECV,
            rtc_configuration=RTC_CONFIG,
            video_processor_factory=AttendanceProcessor,
            media_stream_constraints={"video": True, "audio": False},
            async_processing=True,
        )

        if st.button("STEP 1: START BIOMETRIC CAPTURE"):
            if reg_id.isdigit() and reg_name:
                if ctx.video_processor:
                    ctx.video_processor.reg_id = reg_id
                    ctx.video_processor.reg_name = reg_name
                    ctx.video_processor.capture_count = 0
                    ctx.video_processor.capture_mode = True
                    st.info(f"Capturing face data for {reg_name}... Please look at the camera.")
                else:
                    st.error("Please start the camera stream first!")
            else:
                st.error("Please enter a numeric ID and Name.")

        if st.button("STEP 2: ENROLL & TRAIN SYSTEM"):
            with st.spinner("Training model..."):
                try:
                    # Save to CSV
                    csv_path = "StudentDetails/StudentDetails.csv"
                    new_data = pd.DataFrame([[reg_id, reg_name]], columns=['SERIAL NO.', 'NAME'])
                    if os.path.isfile(csv_path):
                        df = pd.read_csv(csv_path)
                        df = pd.concat([df, new_data]).drop_duplicates().reset_index(drop=True)
                        df.to_csv(csv_path, index=False)
                    else:
                        new_data.to_csv(csv_path, index=False)

                    # Train
                    recognizer = cv2.face.LBPHFaceRecognizer_create()
                    faces, ids = get_images_and_labels("TrainingImage/")
                    if len(faces) == 0:
                        st.error("No image data captured. Please complete Step 1.")
                    else:
                        recognizer.train(faces, np.array(ids))
                        recognizer.save("TrainingImageLabel/Trainner.yml")
                        st.success(f"✅ {reg_name} Enrolled successfully!")
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
    else:
        st.info("No attendance records found for today.")
