/*
Input [X,Y]  with ranges [1000->2000] 2000 full trottle forward 1000 full trottle backward
*/ 
#include <Servo.h>
Servo servoX;
Servo servoY;

int inputX = 1500;
int inputY = 1500;
byte myBuffer[500];

void setup()

{
  Serial.begin(115200);
  while (!Serial);
  delay(1000);
  servoX.attach(12);
  servoY.attach(13);
  Serial.println("Ready");
}

void loop() {
  readInput();
  writeServos();
}

void writeServos() {
  servoX.writeMicroseconds(inputX);
  servoY.writeMicroseconds(inputY);
}

void readInput() {
  int headerMarker = 113;

  if (Serial.available() < 2) {
    return;
  }
  int header = Serial.read();
  if (header != headerMarker) {
    return;
  }
  int buffer_size = Serial.read();


  long start_wait = millis();
  while (Serial.available() < buffer_size) {
    if (millis() - start_wait > 1000) {
      return;
      Serial.println("Aborting...");
    }
  }
  for (int i = 0; i < buffer_size; i++) {
    myBuffer[i] = Serial.read(); 
  }

  inputX = (int)myBuffer[0] + ((int)myBuffer[1]) * 256;
  inputY = (int)myBuffer[2] + ((int)myBuffer[3]) * 256;
  Serial.print("Donne::");
  Serial.print("x:");
  Serial.print(inputX);
  Serial.print("\ty:");
  Serial.println(inputY);
}

void calibrate(Servo servo) {
  int pos = 0;

  for (pos = 1500; pos >= 1000; pos -= 2)
  {
    servo.writeMicroseconds(pos);
    delay(1);
  }

  for (pos = 1000; pos <= 2000; pos += 2)
  {
    servo.writeMicroseconds(pos);
    delay(1);
  }
  for (pos = 2000; pos >= 1500; pos -= 2)
  {
    servo.writeMicroseconds(pos);
    delay(1);
  }
  
}
