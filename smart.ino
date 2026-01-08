#include <ESP32Servo.h> 

// --- UPDATED PIN CONFIGURATION ---
const int PIR_PIN = 4;        // PIR Sensor Output Pin
const int SERVO_PLASTIC = 10;  // Servo for Plastic (A0)
const int SERVO_PAPER = 5;   // Servo for Paper (A3)
const int SERVO_METAL = 9;    // Servo for Metal (A1)

// --- SERVO OBJECTS ---
Servo servoPlastic;
Servo servoPaper;
Servo servoMetal;

// --- VARIABLES ---
unsigned long lastTrigger = 0;  
const long COOLDOWN = 3000;     

void setup() {
  Serial.begin(115200); 
  
  // Setup PIR
  pinMode(PIR_PIN, INPUT);
  
  // Allocate Timers for ESP32 Servos
  ESP32PWM::allocateTimer(0);
  ESP32PWM::allocateTimer(1);
  ESP32PWM::allocateTimer(2);
  ESP32PWM::allocateTimer(3);
  
  // Setup frequency
  servoPlastic.setPeriodHertz(50);
  servoPaper.setPeriodHertz(50);
  servoMetal.setPeriodHertz(50);

  // Attach Pins (Using your new pins)
  servoPlastic.attach(SERVO_PLASTIC, 500, 2400); 
  servoPaper.attach(SERVO_PAPER, 500, 2400);
  servoMetal.attach(SERVO_METAL, 500, 2400);

  // Reset Servos to 0 degrees (Closed)
  servoPlastic.write(0);
  servoPaper.write(0);
  servoMetal.write(0);

  delay(2000); // Wait for sensors to stabilize
}

void loop() {
  // 1. READ PIR SENSOR
  int motion = digitalRead(PIR_PIN);

  // If motion detected AND cooldown passed
  if (motion == HIGH && (millis() - lastTrigger > COOLDOWN)) {
    Serial.println("CHECK"); // Wake up Python
    lastTrigger = millis();  
  }

  // 2. LISTEN FOR PYTHON COMMANDS
  if (Serial.available() > 0) {
    char command = Serial.read(); 

    if (command == '1') {
      moveServo(servoPlastic); // Sort Plastic
    } 
    else if (command == '2') {
      moveServo(servoPaper);   // Sort Paper
    } 
    else if (command == '3') {
      moveServo(servoMetal);   // Sort Metal
    }
  }
}

// --- HELPER FUNCTION ---
void moveServo(Servo &myServo) {
  myServo.write(90);  // Open to 90 degrees
  delay(2000);        // Wait 2 seconds
  myServo.write(0);   // Close back to 0
}