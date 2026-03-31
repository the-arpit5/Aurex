# INSTALLATION REQUIREMENT:
# Run these commands in your terminal to enable face recognition:
# 1. pip uninstall opencv-python
# 2. pip install opencv-contrib-python

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as mess
import tkinter.simpledialog as tsd
import cv2
import os
import csv
import numpy as np
from PIL import Image
import pandas as pd
import datetime
import time

# --- Path Initialization ---
def assure_path_exists(path):
    dir = os.path.dirname(path)
    if not os.path.exists(dir):
        os.makedirs(dir)

# --- Logic Functions ---

def tick():
    time_string = time.strftime('%H:%M:%S')
    clock.config(text=time_string)
    clock.after(200, tick)

def contact():
    mess.showinfo(title='Contact us', message="Please contact us on: 'shubhamkumar8180323@gmail.com'")

def check_haarcascadefile():
    exists = os.path.isfile("haarcascade_frontalface_default.xml")
    if not exists:
        mess.showerror(title='File Missing', message='haarcascade_frontalface_default.xml not found. Please add it to the project folder.')
        window.destroy()

def save_pass():
    assure_path_exists("TrainingImageLabel/")
    exists1 = os.path.isfile("TrainingImageLabel/psd.txt")
    if exists1:
        with open("TrainingImageLabel/psd.txt", "r") as tf:
            key = tf.read()
    else:
        new_pas = tsd.askstring('Setup Password', 'Please enter a new admin password:', show='*')
        if new_pas is None:
            mess.showwarning(title='Warning', message='Password not set!!')
            return
        else:
            with open("TrainingImageLabel/psd.txt", "w") as tf:
                tf.write(new_pas)
            mess.showinfo(title='Success', message='Password registered successfully!!')
            return

    op = old.get()
    newp = new.get()
    nnewp = nnew.get()
    
    if op == key:
        if newp == nnewp:
            with open("TrainingImageLabel/psd.txt", "w") as txf:
                txf.write(newp)
            mess.showinfo(title='Success', message='Password changed successfully!!')
            master.destroy()
        else:
            mess.showerror(title='Error', message='Passwords do not match!')
    else:
        mess.showerror(title='Error', message='Incorrect old password.')

def change_pass():
    global master, old, new, nnew
    master = tk.Toplevel()
    master.geometry("400x260")
    master.resizable(False, False)
    master.title("Security Settings")
    master.configure(background="white")
    
    main_lbl = tk.Label(master, text="Update Admin Password", bg="white", fg="#1e293b", font=('Segoe UI', 12, 'bold'))
    main_lbl.pack(pady=15)
    
    def create_pop_input(label):
        tk.Label(master, text=label, bg="white", fg="#64748b", font=('Segoe UI', 9)).pack()
        e = tk.Entry(master, width=30, fg="#1e293b", font=('Segoe UI', 10), show='*', bd=1, relief="solid")
        e.pack(pady=(0, 10))
        return e

    old = create_pop_input("Current Password")
    new = create_pop_input("New Password")
    nnew = create_pop_input("Confirm New Password")
    
    btn_frame = tk.Frame(master, bg="white")
    btn_frame.pack(pady=10)
    
    save1 = tk.Button(btn_frame, text="Update", command=save_pass, fg="white", bg="#4f46e5", width=12, font=('Segoe UI', 9, 'bold'), bd=0, cursor="hand2")
    save1.pack(side="left", padx=5)
    cancel = tk.Button(btn_frame, text="Cancel", command=master.destroy, fg="#475569", bg="#f1f5f9", width=12, font=('Segoe UI', 9, 'bold'), bd=0, cursor="hand2")
    cancel.pack(side="left", padx=5)

def psw():
    assure_path_exists("TrainingImageLabel/")
    exists1 = os.path.isfile("TrainingImageLabel/psd.txt")
    if exists1:
        with open("TrainingImageLabel/psd.txt", "r") as tf:
            key = tf.read()
    else:
        new_pas = tsd.askstring('Setup', 'Please set a new admin password:', show='*')
        if new_pas is None: return
        with open("TrainingImageLabel/psd.txt", "w") as tf:
            tf.write(new_pas)
        mess.showinfo(title='Success', message='Password set successfully!!')
        return
            
    password = tsd.askstring('Admin Access', 'Enter Password:', show='*')
    if password == key:
        TrainImages()
    elif password is not None:
        mess.showerror(title='Access Denied', message='Wrong password entered.')

def clear():
    txt.delete(0, 'end')
    message.configure(text="Ready to register...")

def clear2():
    txt2.delete(0, 'end')
    message.configure(text="Ready to register...")

def TakeImages():
    check_haarcascadefile()
    columns = ['SERIAL NO.', '', 'ID', '', 'NAME']
    assure_path_exists("StudentDetails/")
    assure_path_exists("TrainingImage/")
    serial = 0
    exists = os.path.isfile("StudentDetails/StudentDetails.csv")
    if exists:
        with open("StudentDetails/StudentDetails.csv", 'r') as csvFile1:
            reader1 = csv.reader(csvFile1)
            for l in reader1:
                serial = serial + 1
        serial = (serial // 2)
    else:
        with open("StudentDetails/StudentDetails.csv", 'a+') as csvFile1:
            writer = csv.writer(csvFile1)
            writer.writerow(columns)
            serial = 1
            
    Id = txt.get()
    name = txt2.get()
    
    if (name.replace(' ', '').isalpha()):
        cam = cv2.VideoCapture(0)
        detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
        sampleNum = 0
        while True:
            ret, img = cam.read()
            if not ret: break
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = detector.detectMultiScale(gray, 1.3, 5)
            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x + w, y + h), (79, 70, 229), 2)
                sampleNum = sampleNum + 1
                cv2.imwrite(f"TrainingImage/{name}.{serial}.{Id}.{sampleNum}.jpg", gray[y:y + h, x:x + w])
                cv2.imshow('Face Enrollment - Press Q to Cancel', img)
            if cv2.waitKey(100) & 0xFF == ord('q') or sampleNum > 100:
                break
        cam.release()
        cv2.destroyAllWindows()
        
        row = [serial, '', Id, '', name]
        with open('StudentDetails/StudentDetails.csv', 'a+') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow(row)
        message.configure(text=f"Enrollment Complete for: {name}")
        update_registration_count()
    else:
        message.configure(text="Error: Name must be alphabets.")

def TrainImages():
    check_haarcascadefile()
    assure_path_exists("TrainingImageLabel/")
    try:
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        faces, ID = getImagesAndLabels("TrainingImage")
        if len(faces) == 0:
            mess.showwarning(title='No Data', message='No student images found!')
            return
        recognizer.train(faces, np.array(ID))
        recognizer.save("TrainingImageLabel/Trainner.yml")
        message.configure(text="System Trained Successfully")
    except AttributeError:
        mess.showerror(title='System Error', message='Required modules missing. Run: pip install opencv-contrib-python')
    except Exception as e:
        mess.showerror(title='Training Error', message=str(e))

def getImagesAndLabels(path):
    imagePaths = [os.path.join(path, f) for f in os.listdir(path) if f.endswith(('.jpg', '.png'))]
    faces = []
    Ids = []
    for imagePath in imagePaths:
        pilImage = Image.open(imagePath).convert('L')
        imageNp = np.array(pilImage, 'uint8')
        ID = int(os.path.split(imagePath)[-1].split(".")[1])
        faces.append(imageNp)
        Ids.append(ID)
    return faces, Ids

def TrackImages():
    check_haarcascadefile()
    assure_path_exists("Attendance/")
    assure_path_exists("StudentDetails/")
    
    for k in tv.get_children():
        tv.delete(k)
        
    try:
        recognizer = cv2.face.LBPHFaceRecognizer_create()
    except AttributeError:
        mess.showerror(title='OpenCV Error', message='Please install opencv-contrib-python.')
        return

    if os.path.isfile("TrainingImageLabel/Trainner.yml"):
        recognizer.read("TrainingImageLabel/Trainner.yml")
    else: 
        mess.showwarning(title='Missing Data', message='Model not trained. Enrollment required.')
        return
        
    faceCascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    cam = cv2.VideoCapture(0)
    font = cv2.FONT_HERSHEY_SIMPLEX
    col_names = ['Id', '', 'Name', '', 'Date', '', 'Time']
    
    if os.path.isfile("StudentDetails/StudentDetails.csv"):
        df = pd.read_csv("StudentDetails/StudentDetails.csv")
    else:
        mess.showerror(title='System Error', message='Student database not found.')
        cam.release()
        return

    attendance_data = None
    
    while True:
        ret, im = cam.read()
        if not ret: break
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(gray, 1.2, 5)
        for (x, y, w, h) in faces:
            cv2.rectangle(im, (x, y), (x + w, y + h), (79, 70, 229), 2)
            serial, conf = recognizer.predict(gray[y:y + h, x:x + w])
            if conf < 50:
                ts = time.time()
                date = datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y')
                timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                aa = df.loc[df['SERIAL NO.'] == serial]['NAME'].values
                ID = df.loc[df['SERIAL NO.'] == serial]['ID'].values
                ID = str(ID[0]) if len(ID) > 0 else "N/A"
                bb = str(aa[0]) if len(aa) > 0 else "N/A"
                attendance_data = [ID, '', bb, '', str(date), '', str(timeStamp)]
            else:
                bb = 'Unknown'
            cv2.putText(im, str(bb), (x, y + h), font, 0.8, (255, 255, 255), 2)
        
        cv2.imshow('Scanning - Press Q to Finish', im)
        if cv2.waitKey(1) == ord('q'): break
            
    cam.release()
    cv2.destroyAllWindows()

    if attendance_data:
        date = attendance_data[4]
        path = f"Attendance/Attendance_{date}.csv"
        file_exists = os.path.isfile(path)
        with open(path, 'a+') as csvFile1:
            writer = csv.writer(csvFile1)
            if not file_exists:
                writer.writerow(col_names)
            writer.writerow(attendance_data)
        
        if os.path.isfile(path):
            with open(path, 'r') as csvFile1:
                reader1 = csv.reader(csvFile1)
                next(reader1)
                for line in reader1:
                    if len(line) > 6:
                        tv.insert('', 0, values=(line[2], line[4], line[6]))

def update_registration_count():
    res = 0
    try:
        if os.path.isfile("StudentDetails/StudentDetails.csv"):
            with open("StudentDetails/StudentDetails.csv", 'r') as csvFile1:
                reader1 = csv.reader(csvFile1)
                res = sum(1 for row in reader1)
            res = max(0, (res // 2) - 1)
    except:
        res = 0
    message.configure(text=f"Database Size: {res} Students")

# --- UI Setup ---
window = tk.Tk()
window.geometry("1280x720")
window.resizable(True, False)
window.title("Attendance Pro")

# Professional White/Indigo Palette
BG_WINDOW = "#f8fafc"    # Off white
BG_CARD = "#ffffff"      # Pure white
TXT_PRIMARY = "#1e293b"  # Dark Slate
TXT_SECONDARY = "#64748b" # Muted blue/gray
ACCENT = "#4f46e5"       # Indigo
SUCCESS = "#16a34a"      # Green
DANGER = "#dc2626"       # Red
BORDER = "#e2e8f0"       # Light gray

window.configure(background=BG_WINDOW)

# Global Styles
style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview", background="white", foreground=TXT_PRIMARY, fieldbackground="white", rowheight=35, bordercolor=BORDER, font=('Segoe UI', 10))
style.map("Treeview", background=[('selected', "#eef2ff")], foreground=[('selected', ACCENT)])
style.configure("Treeview.Heading", background="#f1f5f9", foreground=TXT_PRIMARY, font=('Segoe UI', 10, 'bold'), borderwidth=1)

# Header
header_frame = tk.Frame(window, bg=BG_CARD, highlightbackground=BORDER, highlightthickness=1)
header_frame.place(relx=0, rely=0, relwidth=1, relheight=0.12)

tk.Label(header_frame, text="Attendance Management System", fg=TXT_PRIMARY, bg=BG_CARD, font=('Segoe UI', 24, 'bold')).pack(pady=(15, 0))

# Clock/Date info
info_frame = tk.Frame(header_frame, bg=BG_CARD)
info_frame.place(relx=0.82, rely=0.2)
date_str = datetime.datetime.now().strftime("%d %B %Y")
datef = tk.Label(info_frame, text=date_str, fg=TXT_SECONDARY, bg=BG_CARD, font=('Segoe UI', 11))
datef.pack(anchor="e")
clock = tk.Label(info_frame, fg=ACCENT, bg=BG_CARD, font=('Segoe UI', 14, 'bold'))
clock.pack(anchor="e")
tick()

# Left Column (Attendance Scanning)
frame1 = tk.Frame(window, bg=BG_CARD, highlightbackground=BORDER, highlightthickness=1)
frame1.place(relx=0.04, rely=0.16, relwidth=0.45, relheight=0.78)

tk.Label(frame1, text="ATTENDANCE OPERATIONS", fg=ACCENT, bg=BG_CARD, font=('Segoe UI', 12, 'bold')).pack(pady=20)

trackImg = tk.Button(frame1, text="LAUNCH ATTENDANCE SCANNER", command=TrackImages, 
                     fg="white", bg=ACCENT, activebackground="#4338ca", 
                     font=('Segoe UI', 11, 'bold'), bd=0, padx=40, pady=12, cursor="hand2")
trackImg.pack(pady=10)

# Treeview Log
tv_container = tk.Frame(frame1, bg="white")
tv_container.pack(fill="both", expand=True, padx=25, pady=(20, 80))

tv = ttk.Treeview(tv_container, height=10, columns=('name', 'date', 'time'), show='headings')
tv.heading('name', text='STUDENT NAME')
tv.heading('date', text='DATE')
tv.heading('time', text='TIME')
tv.column('name', width=150, anchor="center")
tv.column('date', width=100, anchor="center")
tv.column('time', width=100, anchor="center")

scb = ttk.Scrollbar(tv_container, orient="vertical", command=tv.yview)
tv.configure(yscrollcommand=scb.set)
tv.pack(side="left", fill="both", expand=True)
scb.pack(side="right", fill="y")

# Exit
quitWindow = tk.Button(frame1, text="Terminte Session", command=window.destroy, 
                       fg=DANGER, bg="white", highlightbackground=DANGER, highlightthickness=1, 
                       font=('Segoe UI', 10, 'bold'), bd=0, pady=5, width=20, cursor="hand2")
quitWindow.place(relx=0.5, rely=0.92, anchor="center")

# Right Column (Registration)
frame2 = tk.Frame(window, bg=BG_CARD, highlightbackground=BORDER, highlightthickness=1)
frame2.place(relx=0.51, rely=0.16, relwidth=0.45, relheight=0.78)

tk.Label(frame2, text="STUDENT ENROLLMENT", fg=ACCENT, bg=BG_CARD, font=('Segoe UI', 12, 'bold')).pack(pady=20)

def create_styled_input(label, y):
    tk.Label(frame2, text=label, fg=TXT_SECONDARY, bg=BG_CARD, font=('Segoe UI', 10, 'bold')).place(x=50, y=y)
    e = tk.Entry(frame2, font=('Segoe UI', 12), bg="#f8fafc", fg=TXT_PRIMARY, bd=0, highlightthickness=1, highlightbackground=BORDER)
    e.place(x=50, y=y+28, width=350, height=40)
    return e

txt = create_styled_input("STUDENT ID (Numbers)", 80)
txt2 = create_styled_input("STUDENT FULL NAME", 180)

# Clear Buttons
c1 = tk.Button(frame2, text="Clear", command=clear, fg=TXT_SECONDARY, bg="white", bd=0, font=('Segoe UI', 9), cursor="hand2")
c1.place(x=410, y=112)
c2 = tk.Button(frame2, text="Clear", command=clear2, fg=TXT_SECONDARY, bg="white", bd=0, font=('Segoe UI', 9), cursor="hand2")
c2.place(x=410, y=212)

# Action Buttons
takeImg = tk.Button(frame2, text="STEP 1: CAPTURE FACE DATA", command=TakeImages, 
                    fg="white", bg="#6366f1", activebackground="#4f46e5",
                    font=('Segoe UI', 11, 'bold'), width=40, pady=10, bd=0, cursor="hand2")
takeImg.place(x=50, y=300)

trainImg = tk.Button(frame2, text="STEP 2: ENROLL & SAVE PROFILE", command=psw, 
                     fg="white", bg=SUCCESS, activebackground="#15803d",
                     font=('Segoe UI', 11, 'bold'), width=40, pady=10, bd=0, cursor="hand2")
trainImg.place(x=50, y=365)

# Status Footer
message = tk.Label(frame2, text="Ready for new enrollment", bg=BG_CARD, fg=TXT_SECONDARY, font=('Segoe UI', 10, 'italic'))
message.place(x=50, y=435)
update_registration_count()

# Menubar
menubar = tk.Menu(window, bg=BG_CARD, fg=TXT_PRIMARY)
filemenu = tk.Menu(menubar, tearoff=0, bg=BG_CARD, fg=TXT_PRIMARY)
filemenu.add_command(label='Change Password', command=change_pass)
filemenu.add_command(label='Contact Support', command=contact)
filemenu.add_separator()
filemenu.add_command(label='Exit', command=window.destroy)
menubar.add_cascade(label='System Settings', menu=filemenu)

window.configure(menu=menubar)
window.mainloop()
