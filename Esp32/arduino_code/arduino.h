#include <WiFi.h>
#include <HTTPClient.h>
#include <DHT.h>
#include "config.h"  // Include the config file

#define DHT11_PIN 4
DHT dht11(DHT11_PIN, DHT11);

void setup() {
  Serial.begin(115200);
  delay(2000);  
  Serial.println("ESP32 Serial Monitor Test");

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);  // Use config variables

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }

  Serial.println("\nConnected to Wi-Fi");
  Serial.print("ESP32 IP Address: ");
  Serial.println(WiFi.localIP());

  dht11.begin();
}

void loop() {
  float humi = dht11.readHumidity();
  float tempC = dht11.readTemperature();

  if (isnan(humi) || isnan(tempC)) {
    Serial.println("Failed to read from DHT11 sensor!");
    return;
  }

  String jsonData = "{\"humidity\": " + String(humi) + ", \"temperature_c\": " + String(tempC) + "}";

  Serial.println("Sending data: " + jsonData);

  HTTPClient http;

  http.begin(SERVER_URL);  // Use config variable
  http.addHeader("Content-Type", "application/json");

  int httpCode = http.POST(jsonData);

  Serial.print("HTTP Code: ");
  Serial.println(httpCode);

  if (httpCode > 0) {
    String payload = http.getString(); 
    Serial.println("Server Response: " + payload);
  } else {
    Serial.println("Error sending request to server");
  }

  http.end();
  delay(2000);  
}
