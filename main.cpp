#include <ESP8266WiFi.h>
#include "initWiFi.h"
#include <ESP8266WebServer.h>
#include <get_mac.h>
#include "glob.h"

ESP8266WebServer server(8080);
// WiFiServer espServer(8888);

#define LED D0

IPAddress remote_IP(1,1,1,1);
int remote_Port = 9999;
String token;
String control = "speech_openai";
String data_send;

WiFiUDP udp;
unsigned int localPort = 9999;

void setup() {
  Serial.begin(9600);
  Serial.println("🔄 Starting ESP8266...");
  udp.begin(localPort);
  delay(100);
  get_mac();

  // 初始化 GPIO
  pinMode(LED, OUTPUT);
  digitalWrite(LED, HIGH);
  
  server.begin();
  // espServer.begin();

  initWiFi();  // 自訂 WiFi 初始化

  Serial.println(WiFi.localIP());

  server.on("/light/turn_on", []() {
      digitalWrite(LED, LOW);
      server.send(200, "text/plain", "light on");
  });

  server.on("/light/turn_off", []() {
      digitalWrite(LED, HIGH);
      server.send(200, "text/plain", "light off");
  });

}

void data_processing() {
  if (token == "request_mac"){
    // data_send = "{'mac':'"+mac+"','control':'"+control+"','_macback':'macback" + String(WiFi.RSSI())+"'}";
    data_send = "{'mac':'"+mac+"','control':'"+control+"','_macback':'macback'}";
    udp.beginPacket(remote_IP,remote_Port);
    udp.write(data_send.c_str());
    udp.endPacket();
  }
}

void UDP_receive(){
  // Serial.println("UDP_receive");
  int packetSize = udp.parsePacket();  //udn.parsePacket 用來監聽封包的功能
  // Serial.print("packetSize:");Serial.println(packetSize);
  if (packetSize) {   //當有封包進來時, 將內容放進 packetBuffer變數中
    char packetBuffer[512];
    int len = udp.read(packetBuffer, 512);
    if (len > 0) packetBuffer[len - 1] = 0;
    token = String(packetBuffer);
    // Serial.print("token: ");Serial.println(token);
    remote_IP = udp.remoteIP();
    remote_Port = udp.remotePort();
    data_processing();
    token = "";

  }
}



void loop() {

  server.handleClient();
  UDP_receive();
  delay(500);
}