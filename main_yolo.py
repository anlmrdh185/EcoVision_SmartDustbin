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
KEY_FILE = "firebase_key.json.json"

# DATABASE URL 
DATABASE_URL = "https://smartdustbin-61ec7-default-rtdb.firebaseio.com/"  

ARDUINO_PORT = 'COM4'  
BAUD_RATE = 115200

# --- COOLDOWN SETTINGS ---
ACTIVE_TIMEOUT = 10     # How long to stay awake after motion stops
SORTING_COOLDOWN = 5    # Time to wait after sorting an item (in seconds)

# --- 1. CONNECT TO FIREBASE ---
print("Connecting to Firebase...", end=" ")
try:
    if not firebase_admin._apps:
        cred = credentials.Certificate(KEY_FILE)
        firebase_admin.initialize_app(cred, {'databaseURL': DATABASE_URL})
    ref = db.reference('SmartBin_Logs')
    print("SUCCESS! ✅")
except Exception as e:
    print(f"\nFIREBASE ERROR: {e}")
    ref = None

# --- 2. CONNECT TO ARDUINO ---
print("Connecting to Arduino...", end=" ")
try:
    ser = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=0.1)
    time.sleep(2) 
    print("SUCCESS! ✅")
except:
    print("FAILED (Simulation Mode)")
    ser = None

# --- 3. LOAD YOLO MODEL ---
print("Loading YOLO Model...")
try:
    model = YOLO("best.pt")
    classNames = model.names 
    print(f"Classes found: {classNames}")
except Exception as e:
    print(f"MODEL ERROR: {e}")
    exit()

# --- SETUP CAMERA & VARIABLES ---
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

# Counters
total_plastic = 0
total_paper = 0
total_metal = 0

# Variables
system_active = False
last_activity_time = 0
last_sort_time = 0  # To track when we last sorted an item

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
                last_activity_time = time.time() 
        except: pass

    # --- B. SYSTEM ACTIVE LOGIC ---
    if system_active:
        success, img = cap.read()
        if not success: continue

        # --- COOLDOWN CHECK ---
        # If we just sorted something, show a "WAIT" message and skip detection
        time_since_sort = time.time() - last_sort_time
        if time_since_sort < SORTING_COOLDOWN:
            remaining = int(SORTING_COOLDOWN - time_since_sort)
            cvzone.putTextRect(img, f"Sorting... Wait {remaining}s", (50, 50), 
                               scale=2, thickness=2, colorR=(0, 0, 255))
            cv2.imshow("Smart Bin AI", img)
            cv2.waitKey(1)
            continue # Skip the rest of the loop (Detection)

        # Run YOLO
        results = model(img, stream=True, verbose=False)
        
        detected_material = None
        highest_conf = 0

        for r in results:
            boxes = r.boxes
            for box in boxes:
                # Calculate Confidence
                conf = math.ceil((box.conf[0] * 100)) / 100
                
                # Only accept > 80% 
                if conf > 0.8: 
                    last_activity_time = time.time() # Keep system awake
                    
                    cls = int(box.cls[0])
                    currentClass = classNames[cls]
                    
                    # Get Bounding Box 
                    x1, y1, x2, y2 = box.xyxy[0]
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    w, h = x2 - x1, y2 - y1
                    
                    cvzone.putTextRect(img, f'{currentClass} {conf}', (max(0, x1), max(35, y1)), scale=1, thickness=1)

                    if conf > highest_conf:
                        highest_conf = conf
                        detected_material = currentClass

        # --- SORTING LOGIC ---
        if detected_material:
            
            print(f">>> Detected: {detected_material} ({highest_conf*100:.0f}%)")
            category = "Unknown"
            valid_sort = False
            
            # 1. PLASTIC
            if "plastic" in detected_material: 
                print("   -> Action: Sorting PLASTIC (1)")
                if ser: ser.write(b'1')
                total_plastic += 1
                category = "Plastic"
                valid_sort = True

            # 2. PAPER
            elif "paper" in detected_material:
                print("   -> Action: Sorting PAPER (2)")
                if ser: ser.write(b'2')
                total_paper += 1
                category = "Paper"
                valid_sort = True

            # 3. METAL
            elif "metal" in detected_material:
                print("   -> Action: Sorting METAL (3)")
                if ser: ser.write(b'3')
                total_metal += 1
                category = "Metal"
                valid_sort = True
            
            # --- FIREBASE & COOLDOWN TRIGGER ---
            if valid_sort:
                # 1. Trigger the Cooldown
                last_sort_time = time.time()
                print(f"   -> Cooldown started for {SORTING_COOLDOWN} seconds...")

                # 2. Upload to Firebase
                if ref:
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
                        print("   -> Firebase Uploaded!")
                    except Exception as e:
                        print(f"   -> Upload Failed: {e}")

        # Show the Window
        cv2.imshow("EcoVision", img)
        
        # TIMEOUT CHECK
        if time.time() - last_activity_time > ACTIVE_TIMEOUT:
            print(">>> Timeout reached. System Sleeping... zzz")
            system_active = False
            cv2.destroyAllWindows() 

        # Exit Key
        if cv2.waitKey(1) == 27: # ESC
            break
    
    else:
        # Sleeping...
        time.sleep(0.1) 

cap.release()
cv2.destroyAllWindows()

cap.release()

cv2.destroyAllWindows()



