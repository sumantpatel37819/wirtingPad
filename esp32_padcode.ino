#include <WiFi.h>                  // ESP32 WiFi library
#include <WiFiUdp.h>              // UDP support for ESP32
#include <Adafruit_GFX.h>         // Core graphics library
#include <Adafruit_SSD1306.h>     // SSD1306 OLED display driver (I2C)

// OLED display configuration
#define SCREEN_WIDTH 128          // OLED display width in pixels
#define SCREEN_HEIGHT 64          // OLED display height in pixels
#define OLED_RESET -1             // No reset pin used (-1 = share Arduino reset)

// WiFi credentials
const char* ssid = "realme narzo 20 Pro";        // WiFi SSID
const char* password = "SumantPatel22"; // WiFi password

// UDP configuration
WiFiUDP udp;                       // Create a UDP object
const int udpPort = 12345;         // Port to listen for incoming UDP packets

// Initialize the SSD1306 OLED display object with I2C communication
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

void setup() {
  Serial.begin(115200);           // Start serial communication for debugging

  // Initialize the OLED display with power settings and I2C address (0x3C is default)
  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println(F("SSD1306 allocation failed"));
    for(;;); // Halt if display initialization fails
  }

  display.clearDisplay();         // Clear internal buffer
  display.display();              // Push buffer to the screen (actually clears screen)
  display.setRotation(0);         // Set screen rotation (0 = normal orientation)

  // Connect to WiFi network
  Serial.print("Connecting to WiFi: ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);     // Start connection attempt

  // Wait until connected
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  // Connected!
  Serial.println("\nConnected to WiFi!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());  // Print assigned IP address

  // Start listening on the specified UDP port
  udp.begin(udpPort);
  Serial.printf("Listening on UDP port %d\n", udpPort);
}

void loop() {
  int packetSize = udp.parsePacket(); // Check if a UDP packet has been received

  if (packetSize) { // If there's a packet
    char incomingPacket[255]; // Buffer to store incoming data
    int len = udp.read(incomingPacket, sizeof(incomingPacket) - 1); // Read the packet

    if (len > 0) {
      incomingPacket[len] = '\0'; // Null-terminate the received string
    }

    // Check for clear command
    if (strcmp(incomingPacket, "clear") == 0) {
      display.clearDisplay();
      display.display();
      Serial.println("Screen cleared");
      return;
    }

    // Declare variables to store parsed values
    int x, y, state;

    // Attempt to parse the packet in format: "x,y,state"
    int parsedItems = sscanf(incomingPacket, "%d,%d,%d", &x, &y, &state);

    Serial.print("Received packet: ");
    Serial.println(incomingPacket);

    // If the parsing is successful and the coordinates are valid
    if (parsedItems == 3 && x >= 0 && x < SCREEN_WIDTH && y >= 0 && y < SCREEN_HEIGHT) {
      // Draw the pixel: white if state=1, black if state=0
      display.drawPixel(x, y, state ? SSD1306_WHITE : SSD1306_BLACK);
      display.display(); // Push changes to the actual display
    } else {
      // If packet is invalid or out of bounds
      Serial.println("Error: Invalid packet format or out of bounds coordinates.");
      Serial.printf("Parsed: x=%d, y=%d, state=%d\n", x, y, state);
    }
  }
}
