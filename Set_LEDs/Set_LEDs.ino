#include <FastLED.h>

// Defines
#define LED_PIN     6
#define NUM_LEDS    60
#define BRIGHTNESS  10  // Range: 0 to 255

// Structs
CRGB leds[NUM_LEDS];

// Variables
int LED_Packet[] = {3, 255, 0, 0, 10, 255, 10, 20, 20, 255, -1}; // Format [Seg_#n,R_0,G_0,B_0,...,R_n-1,G_n-1,B_n-1,-1]

// Prototypes
void random_colors(int data[]);

// Setup
void setup() {
  Serial.begin(9600);
  randomSeed(analogRead(0));
  FastLED.addLeds<WS2812, LED_PIN, GRB>(leds, NUM_LEDS);
  FastLED.setBrightness(BRIGHTNESS);  // Set global brightness here
}

// Main Loop
void loop() {
  color_segments(LED_Packet);
}

// Functions
void color_segments(int data[]) {
  /*
    Divide up the strip into n=data[0] equal segments (groups of LEDs)
    For each segment, set the LEDs to data[n,n+1,n+2] color (r,g,b)  
  */
  int num_Of_Segs = data[0]; // Extract the # of segments (ex. 3)
  int LEDs_Per_Seg = NUM_LEDS / num_Of_Segs; // Evenly group LEDs into each segment (ex. 20)

  int valid_Segs = 0;
  for (int i = 1; data[i] != -1; i += 3) { // Count valid segments until we hit -1
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
  for (int i = 0; i < NUM_LEDS; i+=3) {
    leds[i] = CRGB(255, 0, 0);   // Led 0 = Red
    leds[i+1] = CRGB(0, 255, 0); // Led 1 = Green
    leds[i+2] = CRGB(0, 0, 255); // Led 2 = Blue
  }
  FastLED.show();
  delay(50);  // Wait 
}