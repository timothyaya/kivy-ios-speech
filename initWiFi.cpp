#include <Arduino.h>
#include <initWiFi.h>
#include <WiFiManager.h>

WiFiManager wifiManager;

void initWiFi() {
  // 如果尚未連線 WiFi，則開啟 WiFiManager 設定模式
  Serial.println("🔄 Initializing WiFi...");
  if (WiFi.status() != WL_CONNECTED) {
    wifiManager.setTimeout(360);  // 設定360秒timeout
    // wifiManager.resetSettings(); 
    Serial.println("Attempting WiFi autoConnect...");

    // 嘗試自動連線，失敗會返回 false
    if (!wifiManager.autoConnect("ESP APP")) {
      Serial.println("⚠️ Failed to connect or config timeout, restarting...");
      delay(1000);  // 等一下讓 Serial 資料印出來
      ESP.restart();  // 重啟裝置
    }
  }

  Serial.println();
  Serial.print("✅ Connected. IP: ");
  Serial.println(WiFi.localIP());
  delay(500);
}
