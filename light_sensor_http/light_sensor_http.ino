#include <Arduino.h>

#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>
#include "ESP8266TimerInterrupt.h"
#define TIMER_INTERVAL_MS       2000

WiFiClient client;
HTTPClient http;
ESP8266Timer ITimer;
int count = 0;
int lastCount = -1;
bool skip = false;


void ICACHE_RAM_ATTR TimerHandler() {
  Serial.println("DDDDDD");
  lastCount = count;
  count = 0;
  skip = false;
}

void setup() {
  Serial.begin(115200);
  WiFi.begin("j", "JjJjJjJj");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  ITimer.attachInterruptInterval(TIMER_INTERVAL_MS * 1000, TimerHandler);
}



void callApi() {
  Serial.print("CALL API ");
  Serial.println(lastCount, DEC);
  if (WiFi.status() == WL_CONNECTED) {
    
    if (http.begin(client, "http://192.168.1.41:8080/?value=" + String(lastCount, DEC) )) {  // HTTP
      int httpCode = http.GET();  
      String payload = http.getString();  //Get the response payload
    
      Serial.println(httpCode);   //Print HTTP return code
      Serial.println(payload);    //Print request response payload
    
      http.end();  //Close connection
    } else {
      Serial.printf("[HTTP} Unable to connect\n");
    }
    
  } else {
    Serial.println("Disconnected");
  }
}



void loop() {
  int value = analogRead(A0);     // CANT READ TOO FAST OTHERWISE WIFI GOT DISCONNECTED
  delay(3);
  if (value < 500){
    if (!skip) {
      ++count;
      skip = true;  
    }
  } else {
    skip = false; 
  }

  if (lastCount > -1) {
    callApi();  
    lastCount = -1;
  }
}
