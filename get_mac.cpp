#include <get_mac.h>
#include <ESP8266WiFi.h>

String mac = "";

void get_mac(){
  for(int i=0;i <WiFi.macAddress().length() ; i++){
    if(WiFi.macAddress().substring(i,i+1)!=":"){
      mac = mac+WiFi.macAddress().substring(i,i+1);
    }
  }
  Serial.println(mac);

}