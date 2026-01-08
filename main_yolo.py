import cv2
import cvzone
import math
import serial
import time
import os
from ultralytics import YOLO
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from datetime import datetime

# --- CONFIGURATION: FIREBASE ---
# 1. Your Key File
KEY_FILE = "firebase_key.json.json"

# 2. YOUR DATABASE URL (PASTE IT HERE!)
# Example: "https://your-project.asia-southeast1.firebasedatabase.app/"
DATABASE_URL = "https://smartdustbin-61ec7-default-rtdb.firebaseio.com/"  

ARDUINO_PORT = 'COM4'  # Check your port!
BAUD_RATE = 115200

# --- 1. CONNECT TO FIREBASE ---
print("Connecting to Firebase...", end=" ")
try:
    if not firebase_admin._apps:
        cred = credentials.Certificate(KEY_FILE)
        firebase_admin.initialize_app(cred, {'databaseURL': DATABASE_URL})
    ref = db.reference('SmartBin_Logs')
    print("SUCCESS! ✅")
except Exception as e:
    print(f"\n❌ FIREBASE ERROR: {e}")
    # We continue even if Firebase fails, so hardware still works
    ref = None

# --- 2. CONNECT TO ARDUINO ---
print("Connecting to Arduino...", end=" ")
try:
    ser = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=0.1)
    time.sleep(2) # Allow Arduino to reset
    print("SUCCESS! ✅")
except:
    print("⚠️ FAILED (Simulation Mode)")
    ser = None

# --- 3. LOAD YOLO MODEL ---
print("Loading YOLO Model...")
try:
    model = YOLO("best.pt")
    classNames = model.names 
    print(f"Classes found: {classNames}")
except Exception as e:
    print(f"❌ MODEL ERROR: {e}")
    exit()

# --- SETUP CAMERA & VARIABLES ---
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

# Counters
total_plastic = 0
total_paper = 0
total_metal = 0

# "Pop Out" Logic Variables
system_active = False
last_activity_time = 0
ACTIVE_TIMEOUT = 10  # Seconds to stay open after motion stops
last_upload_time = 0

print("\n--- SYSTEM READY ---")
print("Waiting for Motion (PIR)...")

while True:
    # --- A. CHECK FOR PIR TRIGGER ---
    if ser and ser.in_waiting > 0:
        try:
            line = ser.readline().decode('utf-8').strip()
            if line == "CHECK": 
                print("\n>>> MOTION DETECTED! Activating System...")
                system_active = True
                last_activity_time = time.time() # Reset sleep timer
        except: pass

    # --- B. MANUAL TEST (Press 's' to simulate PIR) ---
    # We need to use cv2.waitKey even if window is closed to capture keys
    # But waitKey only works if a window exists. 
    # So we check keyboard only if system is ACTIVE or via input() if needed.
    # For now, we rely on PIR.

    # --- C. SYSTEM ACTIVE LOGIC ---
    if system_active:
        success, img = cap.read()
        if not success: continue

        # Run YOLO
        results = model(img, stream=True, verbose=False)
        
        detected_material = None
        highest_conf = 0

        for r in results:
            boxes = r.boxes
            for box in boxes:
                conf = math.ceil((box.conf[0] * 100)) / 100
                
                if conf > 0.5: 
                    # If we see ANY object, extend the "Awake" time
                    last_activity_time = time.time()
                    
                    cls = int(box.cls[0])
                    currentClass = classNames[cls]
                    
                    # Draw UI
                    x1, y1, x2, y2 = box.xyxy[0]
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    w, h = x2 - x1, y2 - y1
                    cvzone.cornerRect(img, (x1, y1, w, h))
                    cvzone.putTextRect(img, f'{currentClass} {conf}', (max(0, x1), max(35, y1)), scale=1, thickness=1)

                    if conf > highest_conf:
                        highest_conf = conf
                        detected_material = currentClass

        # --- SORTING LOGIC ---
        # We upload only once every 2 seconds to avoid spamming
        if detected_material and (time.time() - last_upload_time > 2):
            
            print(f">>> Detected: {detected_material} ({highest_conf*100:.0f}%)")
            category = "Unknown"
            
            # 1. PLASTIC (Check using lowercase 'plastic')
            if "plastic" in detected_material: 
                print("   -> Action: Sorting PLASTIC (1)")
                if ser: ser.write(b'1')
                total_plastic += 1
                category = "Plastic"

            # 2. PAPER (Check using lowercase 'paper')
            elif "paper" in detected_material:
                print("   -> Action: Sorting PAPER (2)")
                if ser: ser.write(b'2')
                total_paper += 1
                category = "Paper"

            # 3. METAL (Check using lowercase 'metal')
            elif "metal" in detected_material:
                print("   -> Action: Sorting METAL (3)")
                if ser: ser.write(b'3')
                total_metal += 1
                category = "Metal"
                
            else:
                category = "Other"

            # Firebase Upload
            if ref and category != "Unknown":
                data = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "detected_object": detected_material,
                    "category": category,
                    "confidence": f"{int(highest_conf*100)}%",
                    "counts": {
                        "plastic": total_plastic,
                        "paper": total_paper,
                        "metal": total_metal
                    }
                }
                try:
                    ref.push(data)
                    print("   -> 🔥 Firebase Uploaded!")
                    last_upload_time = time.time()
                except Exception as e:
                    print(f"   -> ❌ Upload Failed: {e}")

        # Show the Window
        cv2.imshow("Smart Bin AI", img)
        
        # TIMEOUT CHECK: Have we been idle too long?
        if time.time() - last_activity_time > ACTIVE_TIMEOUT:
            print(">>> Timeout reached. System Sleeping... zzz")
            system_active = False
            cv2.destroyAllWindows() # Close the window ("Pop In")

        # Exit Key
        if cv2.waitKey(1) == 27: # ESC
            break
    
    else:
        # System is SLEEPING. 
        # We just loop fast and listen to Serial (Line 73)
        time.sleep(0.1) # Save CPU

cap.release()
cv2.destroyAllWindows()