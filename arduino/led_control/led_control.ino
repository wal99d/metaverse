/*
 * LED Control via Serial Communication
 * 
 * Instructions:
 * 1. Connect an LED to pin 13 (or use the built-in LED)
 * 2. Upload this sketch to your Arduino UNO
 * 3. Open Serial Monitor (Tools > Serial Monitor)
 * 4. Set baud rate to 9600
 * 5. Send "LED_ON" or "LED_OFF" to control the LED
 */

const int LED_PIN = 13;      // Using built-in LED on pin 13
String inputString = "";     // String to hold incoming data
boolean stringComplete = false;  // Whether the string is complete

void setup() {
  // Initialize serial communication
  Serial.begin(9600);
  
  // Initialize LED pin as output
  pinMode(LED_PIN, OUTPUT);
  
  // Initialize input string
  inputString.reserve(200);
}

void loop() {
  // Process completed command if available
  if (stringComplete) {
    // Remove any whitespace
    inputString.trim();
    
    // Process commands
    if (inputString == "LED_ON") {
      digitalWrite(LED_PIN, HIGH);
      Serial.println("LED turned on");
    }
    else if (inputString == "LED_OFF") {
      digitalWrite(LED_PIN, LOW);
      Serial.println("LED turned off");
    }
    else {
      Serial.println("Unknown command");
    }
    
    // Clear the string for next command
    inputString = "";
    stringComplete = false;
  }
}

// SerialEvent occurs whenever new data comes in the hardware serial RX
void serialEvent() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    
    // Add character to input string
    if (inChar != '\n') {
      inputString += inChar;
    }
    // Set flag when newline received
    else {
      stringComplete = true;
    }
  }
}