/*
 * D.R.E.N. - Distributed RF Emulation Network
 * Module: 802.11 Raw Beacon Injector
 * Description: Constructs and injects dynamic Wi-Fi beacon frames 
 * with proper tagged parameters (SSID, Rates, Channel) and live timestamps.
 */

#include <Arduino.h>
#include <WiFi.h>
#include <esp_wifi.h>
#include "mac_profiles.h"

// Глобальний лічильник для імітації живого радіотрафіку
uint16_t sequence_number = 0;

// Ініціалізація Wi-Fi з перевіркою статусу (Error Handling)
bool setup_beacon_generator() {
    if (WiFi.mode(WIFI_STA) != true) {
        Serial.println("[!] Помилка: Не вдалося встановити режим WIFI_STA");
        return false;
    }
    
    // Переводимо інтерфейс у режим ін'єкції/моніторингу
    esp_err_t err = esp_wifi_set_promiscuous(true);
    if (err != ESP_OK) {
        Serial.printf("[!] Помилка Promiscuous mode: %s\n", esp_err_to_name(err));
        return false;
    }
    
    Serial.println("[*] Радіоінтерфейс успішно ініціалізовано для ін'єкції");
    return true;
}

// Формування та відправка 100% валідного Beacon пакету
void transmit_spoofed_beacon(const UAVSignature& profile) {
    uint8_t packet[128]; 
    memset(packet, 0, sizeof(packet)); // Очищаємо буфер для ізоляції даних

    // 1. MAC Header (Frame Control & Addresses)
    packet[0] = 0x80; // Beacon frame
    packet[1] = 0x00;
    for(int i=0; i<6; i++) packet[4+i] = 0xFF; // Destination: Broadcast
    for(int i=0; i<6; i++) {
        packet[10+i] = profile.mac[i]; // Source MAC
        packet[16+i] = profile.mac[i]; // BSSID
    }

    // 2. Sequence Control (Динамічний інкремент)
    packet[22] = (sequence_number & 0x0F) << 4; 
    packet[23] = (sequence_number & 0xFF0) >> 4;
    sequence_number = (sequence_number + 1) % 4096; // 12-бітний лічильник

    // 3. Timestamp (Живий час роботи мікроконтролера в мікросекундах)
    uint64_t current_time = esp_timer_get_time();
    memcpy(&packet[24], &current_time, 8);

    // 4. Fixed Parameters (Interval & Capabilities)
    packet[32] = 0x86; // ~400ms в одиницях TU (Time Units)
    packet[33] = 0x01;
    packet[34] = 0x21; // Базові Capabilities
    packet[35] = 0x04;

    int packet_length = 36; // Базовий розмір заголовка

    // 5. Tagged Parameter: SSID (Динамічна вставка з профілю)
    if (profile.ssid != nullptr) {
        int ssid_len = strlen(profile.ssid);
        if (ssid_len > 32) ssid_len = 32; // Ліміт стандарту 802.11
        
        packet[packet_length++] = 0x00; // Tag: SSID
        packet[packet_length++] = ssid_len;
        memcpy(&packet[packet_length], profile.ssid, ssid_len);
        packet_length += ssid_len;
    }

    // 6. Tagged Parameter: Supported Rates (Обов'язково для "реалістичності")
    packet[packet_length++] = 0x01; // Tag: Rates
    packet[packet_length++] = 0x04; // Length: 4 bytes
    packet[packet_length++] = 0x82; // 1 Mbps
    packet[packet_length++] = 0x84; // 2 Mbps
    packet[packet_length++] = 0x8B; // 5.5 Mbps
    packet[packet_length++] = 0x96; // 11 Mbps

    // 7. Tagged Parameter: DS Parameter Set (Канал)
    packet[packet_length++] = 0x03; // Tag: Channel
    packet[packet_length++] = 0x01; // Length: 1 byte
    packet[packet_length++] = profile.channel;

    // 8. Фізична ін'єкція з динамічною довжиною пакета
    esp_err_t result = esp_wifi_80211_tx(WIFI_IF_STA, packet, packet_length, false);
    
    if (result != ESP_OK) {
        Serial.printf("[!] TX Помилка: %s\n", esp_err_to_name(result));
    }
}
