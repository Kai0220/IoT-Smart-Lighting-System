#include <IRremote.h>

// Pin Definitions
int buttonPin = 7;
int infraredPin = 6;
int ldrPin = A0;
int room1level1Pin = 8;
int room1level2Pin = 12;
int room1level3Pin = 11;
int triPin = 5;
int echoPin = 4;

int room2level1Pin = 3;
int room2level2Pin = 2;
int room2level3Pin = 10;

// Represent Different Room
int RoomNum=1;

// State Variables
int brightnessLevel = 1;  // Start at brightness level 1
bool relayState = false;
bool led2State = false;
bool led3State = false;
bool buttonActivate = true;
bool IRActivate = true;
bool LDRActivate = false;
bool UltrasonicSensorActivate = false;

// Timing Variables
unsigned long lastButtonPressTime = 0;
unsigned long buttonPressInterval = 500;  // Minimum interval between button presses (in milliseconds)
unsigned long lastLDRReadTime = 0;
unsigned long ldrReadInterval = 6000;  // Interval between LDR readings (in milliseconds)
unsigned long lastUltrasonicReadTime = 0;
unsigned long UltrasonicReadInterval = 6000;  // Interval between motion sensor readings (in milliseconds)
int distanceTrigger = 10;

//automation rules
int AverageBrightness = 1;
bool advancedAutomation = false;

//energy comsumption
unsigned long lastRelayOnTime = 0;
float energyConsumed = 0.0;
bool energyPrinted = true;  // Flag to track if energy consumption has been printed

// IR Receiver
IRrecv irReceiver(infraredPin);
decode_results irResults;

void setup() {
  Serial.begin(9600);
  pinMode(buttonPin, INPUT_PULLUP);
  pinMode(room1level1Pin, OUTPUT);
  pinMode(room1level2Pin, OUTPUT);
  pinMode(room1level3Pin, OUTPUT);
  pinMode(room2level1Pin, OUTPUT);
  pinMode(room2level2Pin, OUTPUT);
  pinMode(room2level3Pin, OUTPUT);
  irReceiver.enableIRIn();
  pinMode(triPin, OUTPUT);
  pinMode(echoPin, INPUT);
}

void loop() {
  unsigned long currentMillis = millis();
  // Check if the relay is turned off and the last relay on time is valid
  if (!relayState && lastRelayOnTime != 0 && !energyPrinted) {
    // Calculate the time the relay was on
    unsigned long relayOnDuration = currentMillis - lastRelayOnTime;
    // Calculate energy consumed in watt-hours
    energyConsumed = (relayOnDuration / 3600000.0) * getPowerRating();  // Convert milliseconds to hours
    // Reset last relay on time
    lastRelayOnTime = 0;
    // Print energy consumed
    Serial.print("Energy consumed: ");
    Serial.print(energyConsumed, 4);  // Print with 4 decimal places
    Serial.println(" watt-hours");
    // Set the flag to true
    energyPrinted = true;
  }

  // Check for serial commands from Flask server
  if (Serial.available() > 0) {
    char command = Serial.read();
    handleSerialCommand(command);
  }

  if (buttonActivate) {
    handleButtonPress();
  }

  if (IRActivate) {
    handleIRRemote();
  }

  if (currentMillis - lastLDRReadTime >= ldrReadInterval && LDRActivate) {
    detectLDR();
    lastLDRReadTime = currentMillis;
  }

  if (currentMillis - lastUltrasonicReadTime >= UltrasonicReadInterval && UltrasonicSensorActivate) {
    handleUltrasonic();
    lastUltrasonicReadTime = currentMillis;
  }
}
float getPowerRating() {
  // Return the power rating of the light bulb in watts
  return 5.0;
}

void toggleComponents(bool relay, bool led2, bool led3) {

  if (RoomNum == 1) {
    digitalWrite(room1level1Pin, relay ? HIGH : LOW);
    digitalWrite(room1level2Pin, led2 ? HIGH : LOW);
    digitalWrite(room1level3Pin, led3 ? HIGH : LOW);
    relayState = relay;
    led2State = led2;
    led3State = led3;
    // Reset energyPrinted flag when relay is turned on
    if (relay) {
      energyPrinted = false;
    }
  } else if (RoomNum == 2) {
    digitalWrite(room2level1Pin, relay ? HIGH : LOW);
    digitalWrite(room2level2Pin, led2 ? HIGH : LOW);
    digitalWrite(room2level3Pin, led3 ? HIGH : LOW);
    relayState = relay;
    led2State = led2;
    led3State = led3;
    // Reset energyPrinted flag when relay is turned on
    if (relay) {
      energyPrinted = false;
    }
  }
}


void updateBrightness() {
  switch (brightnessLevel) {
    case 1:
      toggleComponents(true, false, false);  // Level 1
      Serial.println("relay_on");
      break;
    case 2:
      toggleComponents(true, true, false);  // Level 2
      Serial.println("level2_on");
      break;
    case 3:
      toggleComponents(true, true, true);  // Level 3
      Serial.println("level3_on");
      break;
    default:
      break;
  }
}

void updateBrightness_forwebsite() {
  switch (brightnessLevel) {
    case 1:
      toggleComponents(true, false, false);  // Level 1
      break;
    case 2:
      toggleComponents(true, true, false);  // Level 2
      break;
    case 3:
      toggleComponents(true, true, true);  // Level 3
      break;
    default:
      break;
  }
}
void handleSerialCommand(char command) {
  String durationValue;
  unsigned long newLdrDuration;
  String durationUltrasonic;
  unsigned long newUltrasonicDuration;
  String distanceValue;
  int newUltrasonicDistance;
  String meanBrightness;
  int newmeanBright;

  switch (command) {
    case '1':  // Command to toggle relay (level 1)
      if (advancedAutomation && (AverageBrightness >= 2 && !relayState)) {
        // If advanced automation is true and average brightness is 2 or higher,
        // directly turn on level 2
        lastRelayOnTime = millis();
        brightnessLevel = 2;
        toggleComponents(true, true, false);
        Serial.println("level2_on");

      } else if (advancedAutomation && (AverageBrightness >= 3 && !relayState)) {
        // If advanced automation is true and average brightness is 3 or higher,
        // directly turn on level 3
        lastRelayOnTime = millis();
        brightnessLevel = 3;
        toggleComponents(true, true, true);
        Serial.println("level3_on");
      } else {
        // If advanced automation is false or average brightness is less than 2,
        // toggle between level 1 and off
        if (!relayState) {
          // If relay is off, set brightness to level 1 and turn on relay
          lastRelayOnTime = millis();
          brightnessLevel = 1;
          toggleComponents(true, false, false);

        } else {
          // If relay is on, toggle relay off
          toggleComponents(false, false, false);
        }
      }
      break;
    case '2':  // Command to increase brightness
      if (relayState && brightnessLevel < 3) {
        brightnessLevel++;
        updateBrightness_forwebsite();
      }
      break;
    case '3':  // Command to decrease brightness
      if (relayState && brightnessLevel > 1) {
        brightnessLevel--;
        updateBrightness_forwebsite();
      }
      break;
    case '4':  // Command to toggle button activation state
      // Toggle button activation state
      buttonActivate = !buttonActivate;
      break;
    case '5':  // Command to toggle IR activation state
      // Toggle IR activation state
      IRActivate = !IRActivate;
      break;
    case '6':
      LDRActivate = !LDRActivate;
      break;
    case '7':  // Command to update LDR duration
      // Read the new LDR duration from the serial input
      durationValue = Serial.readStringUntil('\n');
      newLdrDuration = durationValue.toInt();
      ldrReadInterval = newLdrDuration;
      break;
    case '8':
      UltrasonicSensorActivate = !UltrasonicSensorActivate;
      break;
    case '9':
      // Read the new Ultrasonic duration from the serial input
      durationUltrasonic = Serial.readStringUntil('\n');
      newUltrasonicDuration = durationUltrasonic.toInt();
      UltrasonicReadInterval = newUltrasonicDuration;
      break;
    case '0':
      distanceValue = Serial.readStringUntil('\n');
      newUltrasonicDistance = distanceValue.toInt();
      distanceTrigger = newUltrasonicDistance;
      break;
    case 'a':
      advancedAutomation = !advancedAutomation;
      break;
    case 'b':
      meanBrightness = Serial.readStringUntil('\n');
      newmeanBright = meanBrightness.toInt();
      AverageBrightness = newmeanBright;
      break;

    default:
      break;
  }
}
void handleButtonPress() {
  if (digitalRead(buttonPin) == LOW) {
    unsigned long currentMillis = millis();
    if (currentMillis - lastButtonPressTime >= buttonPressInterval) {
      lastButtonPressTime = currentMillis;
      // Toggle between different states
      if (!relayState) {
        // If relay is off, check advanced automation and average brightness
        if (advancedAutomation && (AverageBrightness == 3)) {
          // If advanced automation is true and average brightness is 3,
          // turn on level 3 directly
          toggleComponents(true, true, true);
          // Send signal over serial indicating level 3 is turned on
          Serial.println("level3_on");
        } else if (advancedAutomation && (AverageBrightness == 2)) {
          // If advanced automation is true and average brightness is 2,
          // turn on level 2 directly
          toggleComponents(true, true, false);
          // Send signal over serial indicating level 2 is turned on
          Serial.println("level2_on");
        } else {
          // If advanced automation is false or average brightness is not 2 or 3,
          // turn on relay (level 1)
          toggleComponents(true, false, false);
          lastRelayOnTime = millis();
          // Send signal over serial indicating relay is turned on
          Serial.println("relay_on");
        }
      } else if (!led2State) {
        // If level 1 is on and level 2 is off, turn on level 2
        toggleComponents(true, true, false);
        // Send signal over serial indicating level 2 is turned on
        Serial.println("level2_on");
      } else if (!led3State) {
        // If level 1 and level 2 are on and level 3 is off, turn on level 3
        toggleComponents(true, true, true);
        // Send signal over serial indicating level 3 is turned on
        Serial.println("level3_on");
      } else {
        // If all levels are on, turn off everything
        toggleComponents(false, false, false);
        // Send signal over serial indicating all levels are turned off
        Serial.println("all_off");
        // Reset energyPrinted flag when all levels are turned off
        energyPrinted = false;
      }
    }
  }
}
void handleIRRemote() {
  if (irReceiver.decode()) {
    // Retrieve the decoded IR data
    unsigned long value = irReceiver.decodedIRData.decodedRawData;
    // Toggle components based on the received IR signal
    if (value == 3091726080) {
      // Toggle relay if it's off, turn off other LEDs
      if (!relayState) {
        if (advancedAutomation && (AverageBrightness == 3)) {
          // If advanced automation is true and average brightness is 3,
          // turn on level 3 directly
          toggleComponents(true, true, true);
          // Update last relay on time
          lastRelayOnTime = millis();
          Serial.println("level3_on");
        } else if (advancedAutomation && (AverageBrightness == 2)) {
          // If advanced automation is true and average brightness is 2,
          // turn on level 2 directly
          toggleComponents(true, true, false);
          // Update last relay on time
          lastRelayOnTime = millis();
          Serial.println("level2_on");
        } else {
          // If advanced automation is false or average brightness is not 2 or 3,
          // turn on relay (level 1)
          toggleComponents(true, false, false);
          // Update last relay on time
          lastRelayOnTime = millis();
          Serial.println("relay_on");
        }
      } else {
        toggleComponents(false, false, false);
        Serial.println("all_off");
      }
    } else if (relayState) {
      if (value == 3927310080) {
        // Increase brightness
        if (brightnessLevel < 3) {
          brightnessLevel++;
          updateBrightness();
        }
      } else if (value == 4161273600) {
        // Decrease brightness
        if (brightnessLevel > 1) {
          brightnessLevel--;
          updateBrightness();
        }
      }
    }
    irReceiver.resume();
  }
}

void detectLDR() {
  int sensorValue = analogRead(ldrPin);
  float voltage = sensorValue * (5.0 / 1023.0);

  Serial.print("Voltage: ");
  Serial.print(voltage);
  Serial.print("V - ");

  if (voltage < 0.5) {
    Serial.println("Very dark");
    Serial.println("level3_on");
    toggleComponents(true, true, true);
    lastRelayOnTime = millis();  // Update the time the light bulb is turned on by the LDR
  } else if (voltage < 1.0) {
    Serial.println("Dark");
    Serial.println("level2_on");
    toggleComponents(true, true, false);
    lastRelayOnTime = millis();  // Update the time the light bulb is turned on by the LDR
  } else if (voltage < 2.5) {
    Serial.println("Not enough Light");
    Serial.println("relay_on");
    toggleComponents(true, false, false);
    lastRelayOnTime = millis();  // Update the time the light bulb is turned on by the LDR
  } else {
    Serial.println("Bright");
    Serial.println("all_off");
    toggleComponents(false, false, false);
  }
}

long microsecondsToCentimeters(long microseconds) {
  // The speed of sound is 340 m/s or 29 microseconds per centimeter.
  // The ping travels out and back, so to find the distance of the object we
  // take half of the distance travelled.
  return microseconds / 29 / 2;
}

long measureDistance(int triggerPin, int echoPin) {
  long duration, cm;
  // The sensor is triggered by a HIGH pulse of 2 or more microseconds.
  // Give a short LOW pulse beforehand to ensure a clean HIGH pulse:
  digitalWrite(triggerPin, LOW);
  delayMicroseconds(2);
  digitalWrite(triggerPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(triggerPin, LOW);
  // Measure the duration of the echo pulse
  duration = pulseIn(echoPin, HIGH);
  // Convert the duration to centimeters
  cm = microsecondsToCentimeters(duration);
  return cm;
}

void handleUltrasonic() {
  long distance = measureDistance(triPin, echoPin);  // Measure the distance
  if (distance >= 0) {                               // Make sure distance measurement is valid
    Serial.print("Distance: ");
    Serial.print(distance);
    Serial.println(" cm");
    if (advancedAutomation) {
      // Check both advanced automation conditions and distance
      if (AverageBrightness == 3 && distance <= distanceTrigger) {
        // If average brightness is 3 and distance is within trigger, turn on level 3 lights
        lastRelayOnTime = millis();
        toggleComponents(true, true, true);
        Serial.println("level3_on");
      } else if (AverageBrightness == 2 && distance <= distanceTrigger) {
        // If average brightness is 2 and distance is within trigger, turn on level 2 lights
        lastRelayOnTime = millis();
        toggleComponents(true, true, false);
        Serial.println("level2_on");
      } else {
        // If distance is not within trigger for advanced automation conditions, check distance only
        if (distance <= distanceTrigger) {
          // If distance is less than or equal to the trigger distance, turn on all lights
          lastRelayOnTime = millis();
          toggleComponents(true, false, false);
          Serial.println("relay_on");
        } else {
          // If distance is greater than the trigger distance, turn off all lights
          toggleComponents(false, false, false);
          Serial.println("all_off");
        }
      }
    } else {
      // If advanced automation is not enabled, use default behavior based on distance only
      if (distance <= distanceTrigger) {
        // If distance is less than or equal to the trigger distance, turn on all lights
        lastRelayOnTime = millis();
        toggleComponents(true, false, false);
        Serial.println("relay_on");
      } else {
        // If distance is greater than the trigger distance, turn off all lights
        toggleComponents(false, false, false);
        Serial.println("all_off");
      }
    }
  } else {
    // Handle invalid distance measurement
    Serial.println("Distance measurement error");
  }
}