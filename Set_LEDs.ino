#include <FastLED.h>

// Defines
#define LED_PIN     6
#define NUM_LEDS    60

// Structs
CRGB leds[NUM_LEDS];

// Variables
int LED_Packet[] = {1, 128, 128, 128, 9999};
uint8_t brightness = 255; // Start at full brightness (0-255)
const int ledPin = 13; // Onboard LED pin for Arduino Mega

// Prototypes
void random_colors(int data[]);
void serial_LED(void);
void parseArray(const String& input, int* data);
void color_segments(int data[]);

// Setup
void setup() {
  Serial.begin(115200);
  FastLED.addLeds<WS2812, LED_PIN, RGB>(leds, NUM_LEDS); // something to consider heree
  FastLED.setBrightness(brightness);  // Set global brightness initially here

}

const int max = 2000;
// main loop
void loop() {
  static char receivedData[max];  // Buffer to hold the incoming string
  static int data[max];           // Array to store parsed integers
  static int index = 0;           // Tracks position in the buffer

  // Check if data is available on the Serial
  while (Serial.available() > 0) {
    char incomingByte = Serial.read();
    
    //Turn the LED on
    // If a newline character is received, process the buffer
    if (incomingByte == '\n') {
      receivedData[index] = '\0';  // Null-terminate the string
      index = 0;                   // Reset the index for the next message

      // Parse the received data into the data array
      parseArray(receivedData, data, max);

      // Call color_segments function with the parsed data
      color_segments(data);
    }

    else {
      // Append incoming byte to the buffer
      if (index < max - 1) {  // Prevent overflow
        receivedData[index++] = incomingByte;
      }

    }
  }

}   



// Functions
void parseArray(const char* input, int* data, int maxSize) {
  int index = 0;  
  int num = 0; 

  for (int i = 0; input[i] != '\0' && index < maxSize; i++) {
    char currentChar = input[i];
    
    // If the current character is a digit, build the number
    if (isdigit(currentChar)) {
      num = num * 10 + (currentChar - '0');
    }
    // If we hit a delimiter (comma), store the number
    else if (currentChar == ',') {
      data[index++] = num; 
      num = 0;  // Reset the number for the next one
    }
  }

  // Store the last number if there is one
  if (num != 0) {
    data[index++] = num;
  }

  // Mark the end of the array with a special value (9999 here)
  data[index] = 9999;
}


// adjust brightness according to rgb values
uint8_t dynamicallyAdjustBrightness(uint8_t r, uint8_t g, uint8_t b) {
    // Perceived brightness formula (human eye sensitivity to color)
  return (uint8_t)(0.2126 * r + 0.7152 * g + 0.0722 * b); 

}




void color_segments(int data[]) {

  int num_Of_Segs = data[0]; // Extract the # of segments
  int LEDs_Per_Seg = NUM_LEDS / num_Of_Segs; // Evenly group LEDs into each segment

  int valid_Segs = 0;
  for (int i = 1; data[i] != 9999; i += 3) { // Count valid segments until we hit -1
    valid_Segs++;
  }


  for (int seg = 0; seg < num_Of_Segs; seg++) { 
    int h = 0, s = 0, v = 0; // Default to black (LED off)
    
    if (seg < valid_Segs) { // The current segment has valid (r,g,b) data
      h = data[seg * 3 + 1]; 
      s = data[seg * 3 + 2]; 
      v = data[seg * 3 + 3]; 
    }

    brightness = dynamicallyAdjustBrightness(s, h, v);
    FastLED.setBrightness(brightness);

    for(int LED = 0; LED < LEDs_Per_Seg; LED++) { 
      int LED_idx = seg * LEDs_Per_Seg + LED; // Calculate the absolute LED index (segment)
      leds[LED_idx] = CRGB(s, h, v); // Set the segments LEDs to a color (r and g switched)
    }

  }
  FastLED.show();

}

void random_colors() {

  for (int i = 0; i < NUM_LEDS; i++) {
    // leds[i] = CRGB(255, 255, 48);   // Led 0 = Red
    leds[i] = CRGB(255, 0, 0);
    // leds[i+1] = CRGB(0, 255, 0); // Led 1 = Green
    // leds[i+2] = CRGB(0, 0, 255); // Led 2 = Blue
  }

  FastLED.show();
  delay(50);  // Wait 
}

void serial_LED() {
  if (Serial.available() > 0) {
    char command = Serial.read(); // Read a single character from the serial port
    if (command == '1') {
      digitalWrite(ledPin, HIGH); // Turn the LED on
      Serial.println("LED is ON");
    } else if (command == '0') {
      digitalWrite(ledPin, LOW); // Turn the LED off
      Serial.println("LED is OFF");
    } else {
      Serial.println("Invalid command. Send '1' to turn ON, '0' to turn OFF.");
    }
  }
}
