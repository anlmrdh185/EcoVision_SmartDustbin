#include <ESP32Servo.h> 

// --- PIN CONFIGURATION ---
const int PIR_PIN = 4;        // PIR Sensor
const int SERVO_PLASTIC = 5;  // Servo Plastic
const int SERVO_PAPER = 10;   // Servo Paper
const int SERVO_METAL = 9;    // Servo Metal

// --- SERVO OBJECTS ---
Servo servoPlastic;
Servo servoPaper;
Servo servoMetal;

// --- VARIABLES ---
unsigned long lastTrigger = 0;  
const long COOLDOWN = 3000;     

void setup() {
  Serial.begin(115200); 
  
  pinMode(PIR_PIN, INPUT);
  
  // Allocate Timers for ESP32
  ESP32PWM::allocateTimer(0);
  ESP32PWM::allocateTimer(1);
  ESP32PWM::allocateTimer(2);
  ESP32PWM::allocateTimer(3);
  
  servoPlastic.setPeriodHertz(50);
  servoPaper.setPeriodHertz(50);
  servoMetal.setPeriodHertz(50);

  // Attach Pins
  servoPlastic.attach(SERVO_PLASTIC, 500, 2400); 
  servoPaper.attach(SERVO_PAPER, 500, 2400);
  servoMetal.attach(SERVO_METAL, 500, 2400);

  // Reset all to 0 (Closed)
  servoPlastic.write(0);
  servoPaper.write(0);
  servoMetal.write(0);

  delay(2000); 
}

void loop() {
  // 1. PIR SENSOR LOGIC
  int motion = digitalRead(PIR_PIN);
  if (motion == HIGH && (millis() - lastTrigger > COOLDOWN)) {
    Serial.println("CHECK"); 
    lastTrigger = millis();  
  }

  // 2. RECEIVE COMMAND FROM PYTHON
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

// --- THIS FUNCTION MAKES IT ROTATE BACK AUTOMATICALLY ---
void moveServo(Servo &myServo) {
  myServo.write(90);    // Action: Move to 0
  delay(2000);         // Wait
  myServo.write(0);  // Reset: Go back to 180
}
