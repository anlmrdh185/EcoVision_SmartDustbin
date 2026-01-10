# EcoVision_SmartDustbin
CPC357: IoT Architecture and Smart Applications  
PROJECT  EcoVision: A Real-Time Intelligent Waste Sorting  and Monitoring System

# Project Description
The Eco Vision Recycle Bin System is an automated waste management solution designed to promote recycling and sustainability. It uses computer vision to detect and classify waste material, automatically sorts it into the correct compartment, and logs the data to the cloud for real-time monitoring.
Unlike traditional bins, this system remains in a "sleep state" to conserve energy, waking up only when the PIR Motion Sensor detects a user. It then uses a custom-trained YOLOv8 AI model to identify the object and an ESP32 microcontroller to actuate servo motors for sorting.

# Key Features
* YOLOv8 Powered: High-speed, real-time detection of waste materials using state-of-the-art AI.
* Intelligent Classification: Distinguishes between Plastic, Paper, and Metal instantly.
* Smart Energy Management: System sleeps automatically and wakes up via PIR sensor interrupts.
* Auto-Sorting Mechanism: Precision servo control to direct waste to the correct bin partition.
* Cloud Logging: All detection data is synced instantly to Google Firebase Realtime Database.
* Live Dashboard: A professional web interface streamlit showing lifetime recycling stats and usage trends.

---
# The AI Model (YOLOv8)
This project relies on the YOLOv8 (You Only Look Once) architecture by Ultralytics, chosen for its superior speed and accuracy in real-time detection.

* Model File: `best.pt` (Custom trained weights included in repo).
* Framework: `ultralytics` Python library.
* Training Classes:
    1.  `Plastic`
    2.  `Paper`
    3.  `Metal`
* Logic: The system filters detections with a confidence score > 80%. If a valid object is found, it triggers the corresponding serial command to the ESP32.

---
# Hardware & Software Requirements

# Hardware Checklist
| Component           | Quantity | Description                              |
| :-----------------: | :------: | :--------------------------------------: |
| Maker Feather ESP32     | 1        | Main Microcontroller                     |
| Servo Motors (SG90) | 3        | Actuators for Plastic, Paper, Metal lids |
| PIR Motion Sensor   | 1        | HC-SR501 for presence detection          |
| Laptop Webcam             | 1        | USB Camera for computer vision           |
| PC / Laptop         | 1        | Runs the Python AI processing unit       |
| Male to Male Wires  | 15       | For connections                          |
| Power Supply        | 4        | 6V external power for servos (1.5v each)            |

# Software Prerequisites
* Python 3.10+ (Required for AI scripts)
* Arduino IDE  (To upload firmware to ESP32)
* Visual Studio Code  (Recommended code editor)
* Google Firebase Account (For cloud database)

---

# Installation & Setup Guide

# Step 1: Hardware Wiring

| Component | Quantity | Description |
| :--- | :---: | :--- |
| Cytron Maker FeatherS3 (or ESP32) | 1 | Main Microcontroller |
| PIR Motion Sensor | 1 | Detects motion to wake up the system |
| Servo Motor (360° ) | 1 | For "Paper" bin lid  |
| Servo Motor (180° ) | 2 | For "Plastic" and "Metal" bin lids |
| Laptop Webcam  | 1 | Connected for AI vision |
| Battery AA (6v) | 4 | External power for servos (with 1.5v each) |
| Breadboard | 1 | For circuit connections |
| Jumper Wires | 15 | Male-to-Male & Male-to-Female |
|Qwicc Cable | 1|To connect PIR Sensor to the Maker Port|

# Step 2: Wiring Connection
| Component | Pin Label (Board) | Wire Color and  Function |
| :--- | :--- | :--- |
| PIR Sensor | D4 | Signal Output|
| PIR Power| VP | VCC (+) |
| PIR Ground | GND | GND (-) |
| | | |
| Servo 1 (Paper)| A3 | Signal (Orange/Yellow wire) |
|Servo 2 (Plastic) | A0 | Signal (Orange/Yellow wire) |
| Servo 3 (Metal) | A1 | Signal (Orange/Yellow wire) |
| | | |
| Servo Power (+) | Breadboard (+) | Connect Red wires to Battery (+) rail |
| Servo Ground (-) | Breadboard (-) | Connect Brown wires to Battery (-) rail |
| Common Ground | GND | Connect Battery (-) to Board GND |
| Battery Holder (+) | Red Wire | Breadboard Positive (+) Rail |
| Battery Holder (-) | Black Wire | Breadboard Negative (-) Rail |

# Step 3: Firmware Setup (Arduino)
1.  Open Arduino IDE.
2.  Install the ESP32 Board Manager.
3.  Go to Sketch > Include Library > Manage Libraries.
4.  Search for and install: `ESP32Servo` by Kevin Harrington.
5.  Open the file `smart.ino` from the `Arduino_Firmware` folder.
6.  Select your Board and Port.
7.  Upload the code.

# Step 4: Python Environment Setup
1.  Ensure Python is installed.
2.  Open your terminal/command prompt in the project folder.
3.  Install the required dependencies:
    pip install ultralytics cvzone pyserial firebase-admin streamlit plotly pandas
    

# Step 5: Firebase Configuration
1.  Go to the [Firebase Console](https://console.firebase.google.com/).
2.  Create a project and enable Realtime Database.
3.  Go to Project Settings > Service Accounts.
4.  Click Generate New Private Key.
5.  Rename the downloaded file to `firebase_key.json` and place it in the project folder.
6.  Open `main_yolo.py` and `dashboard.py`. Update the `DATABASE_URL` variable with your database link.

---

# How to Run the System

We have included a One-Click Launcher to make running the system easy.

1.  Connect your ESP32 to the computer via USB.
2.  Check which COM Port it is using.
3.  Open `main_yolo.py` and update line `ARDUINO_PORT = 'COMX'` to match your port.
4.  Open Dashboard to monitor the recycle items

> What happens next?
>  windows will open automatically.
>  Window : Will show "Waiting for Motion...". Wave your hand at the PIR sensor to activate the camera.

---

# Project Structure

Smart-Dustbin-Project/
│
├── 📜 Start.bat             # One-click system launcher
├── 📜 main_yolo.py          # Main AI Logic & Hardware Communication
├── 📜 dashboard.py          # Streamlit Web Analytics App
├── 📜 best.pt               # Trained YOLOv8 AI Model
├── 📜 smart.ino             # ESP32 Firmware C++ Code
└── 📜 README.md             # Project Documentation
