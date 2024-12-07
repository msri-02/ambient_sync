#include <FastLED.h>

// Defines
#define LED_PIN     6
#define NUM_LEDS    60
#define BRIGHTNESS  50  // Range: 0 to 255

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
  randomSeed(analogRead(0));
  FastLED.addLeds<WS2812, LED_PIN, GRB>(leds, NUM_LEDS);
  FastLED.setBrightness(BRIGHTNESS);  // Set global brightness here
}

//Main Loop
// void loop() {
//   color_segments(LED_Packet);
//   delay(100000);
// }

// Test parser w/ example
// void loop() {
//   static int data[200];  // Array to store parsed integers

//   // Example input string (this would come from Serial in a real scenario)
//   const char* receivedData = "10, 5, 138, 255, 255, 3, 255, 255, 255, 48, 255, 255, 86, 5, 138, 255, 3, 141, 255, 242, 255, 131, 255, 255, 6, 255, 180, 50, 255, 180, 50, 255, 11, 255, 5, 138, 255, 85, 241, 255, 9999]";

//   // Parse the string into the data array
//   parseArray(receivedData, data, 200);

//   // Print the parsed data array (for debugging)
//   Serial.println("Parsed data:");
//   for (int i = 0; data[i] != 9999 && i < 200; i++) {
//     Serial.print(data[i]);
//     Serial.print(" ");
//   }
//   Serial.println();  // New line after printing all data

//   delay(1000);  // Add a delay to slow down the output and prevent excessive printing
// }

// parser + function w/ example
// void loop() {
//   static int data[200];  // Array to store parsed integers

//   // Example input string (this would come from Serial in a real scenario)
//   const char* receivedData = "10, 5, 138, 255, 255, 3, 255, 255, 255, 48, 255, 255, 86, 5, 138, 255, 3, 141, 255, 242, 255, 131, 255, 255, 6, 255, 180, 50, 255, 180, 50, 255, 11, 255, 5, 138, 255, 85, 241, 255, 9999";

//   // Parse the string into the data array
//   parseArray(receivedData, data, 200);

//   // Print the parsed data array (for debugging)
//   Serial.println("Parsed data:");
//   for (int i = 0; data[i] != 9999 && i < 200; i++) {
//     Serial.print(data[i]);
//     Serial.print(" ");
//   }
//   Serial.println();  // New line after printing all data

//   // Call color_segments function with the parsed data
//   color_segments(data);

//   delay(1000);  // Add a delay to slow down the output and prevent excessive printing
// }

// Everything
void loop() {
  static char receivedData[200];  // Buffer to hold the incoming string
  static int data[200];           // Array to store parsed integers
  static int index = 0;           // Tracks position in the buffer

  // Check if data is available on the Serial
  while (Serial.available() > 0) {
    char incomingByte = Serial.read();

    // If a newline character is received, process the buffer
    if (incomingByte == '\n') {
      receivedData[index] = '\0';  // Null-terminate the string
      index = 0;                   // Reset the index for the next message

      // Parse the received data into the data array
      parseArray(receivedData, data, 200);

      // Print the parsed data array (for debugging)
      Serial.println("Parsed data:");
      for (int i = 0; data[i] != 9999 && i < 200; i++) {
        Serial.print(data[i]);
        Serial.print(" ");
      }
      Serial.println();  // New line after printing all data

      // Call color_segments function with the parsed data
      color_segments(data);
    } else {
      // Append incoming byte to the buffer
      if (index < 199) {  // Prevent overflow
        receivedData[index++] = incomingByte;
      }
    }
  }

  delay(100);  // Small delay to prevent overwhelming the Serial input
}


// Functions
void parseArray(const char* input, int* data, int maxSize) {
  int index = 0;  // Array index for storing parsed integers
  int num = 0;    // Variable to hold the current number

  for (int i = 0; input[i] != '\0' && index < maxSize; i++) {
    char currentChar = input[i];
    
    // If the current character is a digit, build the number
    if (isdigit(currentChar)) {
      num = num * 10 + (currentChar - '0');
    }
    // If we hit a delimiter (comma), store the number
    else if (currentChar == ',') {
      data[index++] = num;  // Store the number in the array
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
  /*
    Divide up the strip into n=data[0] equal segments (groups of LEDs)
    For each segment, set the LEDs to data[n,n+1,n+2] color (r,g,b)  
  */
  int num_Of_Segs = data[0]; // Extract the # of segments (ex. 3)
  int LEDs_Per_Seg = NUM_LEDS / num_Of_Segs; // Evenly group LEDs into each segment (ex. 20)

  int valid_Segs = 0;
  for (int i = 1; data[i] != 9999; i += 3) { // Count valid segments until we hit -1
    valid_Segs++;
  }

  for (int seg = 0; seg < num_Of_Segs; seg++) { // Increment per segment
    int r = 0, g = 0, b = 0; // Default to black (LED off)
    
    if (seg < valid_Segs) { // The current segment has valid (r,g,b) data
    r = data[seg * 3 + 1]; // red LED data
    g = data[seg * 3 + 2]; // green LED data
    b = data[seg * 3 + 3]; // blue LED data
    }

    Serial.print("Segment "); Serial.print(seg); 
    Serial.print(": R="); Serial.print(r); 
    Serial.print(", G="); Serial.print(g); 
    Serial.print(", B="); Serial.println(b);

    for(int LED = 0; LED < LEDs_Per_Seg; LED++) { // Increment per LED in a segment
      int LED_idx = seg * LEDs_Per_Seg + LED; // Calculate the absolute LED index (which segment)
      leds[LED_idx] = CRGB(r, g, b); // Set the segments LEDs to a color   
    }

  }
  FastLED.show();

  Serial.print("Valid Segs = "); Serial.println(valid_Segs);
  Serial.print("LEDs/Seg = "); Serial.println(LEDs_Per_Seg); 
  Serial.println("===================================");
}

void random_colors() {
  for (int i = 0; i < NUM_LEDS; i++) {
    leds[i] = CRGB(255, 255, 48);   // Led 0 = Red
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