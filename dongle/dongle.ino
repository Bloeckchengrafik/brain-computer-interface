#include "comms.h"
#include <HardwareSerial.h>

Controller ctrl;

void setup() {
  Serial.begin(115200);
  Serial.println("$$$");
  ctrl.init();
}

void loop() {
  // put your main code here, to run repeatedly:
  // ctrl.update();

  delay(1000);
}

/*
 * Protocol: 
 * 
 * - Everything starts with '$$$'
 * - Lines starting with # are only printed to the console
 * - Lines starting with ! are treated as errors
 * - Lines starting with * are readings
 */
