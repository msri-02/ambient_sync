#include <FastLED.h>

// Defines
#define LED_PIN     6
#define NUM_LEDS    60
#define BRIGHTNESS  255  // Range: 0 to 255

// Structs
CRGB leds[NUM_LEDS];

// Variables
// Format [Seg_#n,R_0,G_0,B_0,...,R_n-1,G_n-1,B_n-1,-1]
int LED_Packet[] = {3, 255, 0, 0, 0, 255, 0, 0, 0, 255, 9999};
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
  FastLED.setBrightness(BRIGHTNESS);  // Set global brightness here
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
      // random_colors();
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


void color_segments(int data[]) {

  int num_Of_Segs = data[0]; // Extract the # of segments (ex. 3)
  int LEDs_Per_Seg = NUM_LEDS / num_Of_Segs; // Evenly group LEDs into each segment (ex. 20)

  int valid_Segs = 0;
  for (int i = 1; data[i] != 9999; i += 3) { // Count valid segments until we hit -1
    valid_Segs++;
  }

  for (int seg = 0; seg < num_Of_Segs; seg++) { // Increment per segment
    int h = 0, s = 0, v = 0; // Default to black (LED off)
    
    if (seg < valid_Segs) {
      h = data[seg * 3 + 1]; // Hue data
      s = data[seg * 3 + 2]; // Saturation data
      v = data[seg * 3 + 3]; // Value (brightness) data
    }

    for(int LED = 0; LED < LEDs_Per_Seg; LED++) { // Increment per LED in a segment
      int LED_idx = seg * LEDs_Per_Seg + LED; // Calculate the absolute LED index (which segment)
      leds[LED_idx] = CRGB(s, h, v); // Set the segments LEDs to a color   
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
  //fill_rainbow(leds, NUM_LEDS, millis() / 10, 5);
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
