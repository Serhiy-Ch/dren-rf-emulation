/*
 * D.R.E.N. - Distributed RF Emulation Network
 * Module: 802.11 Raw Beacon Injector
 * Description: Constructs and injects raw Wi-Fi beacon frames directly 
 * into the RF spectrum to spoof target UAV signatures.
 */

#include <Arduino.h>
#include <WiFi.h>
#include <esp_wifi.h>
#include "mac_profiles.h"

// Шаблон сирого 802.11 Beacon пакету (базовий каркас)
uint8_t raw_beacon_packet[128] = {
    0x80, 0x00, 0x00, 0x00, // Frame Control (Beacon)
    0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, // Destination MAC (Broadcast)
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, // Source MAC (Замінюється динамічно)
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, // BSSID (Замінюється динамічно)
    0x00, 0x00, // Sequence Control
    // Timestamp (8 bytes), Beacon Interval (2 bytes), Capabilities (2 bytes)
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
    0x90, 0x01, // ~400ms Beacon Interval (Hardware info)
    0x21, 0x04
};

// Ініціалізація Wi-Fi інтерфейсу в режимі ін'єкції (Promiscuous Mode)
void setup_beacon_generator() {
    WiFi.mode(WIFI_STA);
    esp_wifi_set_promiscuous(true);
}

// Функція фізичної відправки підробленого сигналу в ефір
void transmit_spoofed_beacon(const DroneProfile& profile) {
    // 1. Динамічно вшиваємо MAC-адресу цілі в наш пакет
    for (int i = 0; i < 6; i++) {
        raw_beacon_packet[10 + i] = profile.mac[i]; // Source MAC
        raw_beacon_packet[16 + i] = profile.mac[i]; // BSSID
    }
    
    // 2. Ін'єкція пакету в радіоефір через низькорівневий API ESP32
    esp_err_t result = esp_wifi_80211_tx(WIFI_IF_STA, raw_beacon_packet, sizeof(raw_beacon_packet), false);
    
    // 3. Вивід у лог для дебагінгу
    if (result == ESP_OK) {
        Serial.printf("[TX] Spoofed Beacon Sent | Target MAC: %02X:%02X:%02X:%02X:%02X:%02X\n",
                      profile.mac[0], profile.mac[1], profile.mac[2],
                      profile.mac[3], profile.mac[4], profile.mac[5]);
    } else {
        Serial.println("[!] TX RF Injection Failed");
    }
}

