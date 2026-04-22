/*
 * D.R.E.N. - Distributed RF Emulation Network
 * Module: Main Controller
 * Description: The central nervous system uniting the Jitter Engine, 
 * MAC Profiles, and Beacon Generator to execute the emulation loop.
 */

#include <Arduino.h>
#include "mac_profiles.h"

// Forward declarations для доступу до зовнішніх C++ модулів
extern void setup_jitter_engine(bool deterministic = false);
extern uint32_t get_next_delay_us();
extern bool setup_beacon_generator();
extern void transmit_spoofed_beacon(const UAVSignature& profile);

void setup() {
    // Відкриваємо серійний порт для логування
    Serial.begin(115200);
    delay(1000); // Даємо час монітору порту підключитися
    
    Serial.println("\n[***] D.R.E.N. Node Initialization [***]");

    // 1. Запускаємо генератор інтервалів із живим TRNG
    setup_jitter_engine(false);
    Serial.println("[*] Jitter Engine: Online");

    // 2. Переводимо радіоантену в бойовий режим ін'єкції
    if (!setup_beacon_generator()) {
        Serial.println("[!] Critical Radio Error. System Halted.");
        while(true) { delay(1000); } // Жорстке блокування при фатальній помилці
    }
    
    Serial.println("[***] System Ready. Executing Spoofing Sequence [***]\n");
}

void loop() {
    // 1. Отримуємо наступний стохастичний інтервал
    uint32_t current_delay_us = get_next_delay_us();
    
    // 2. Розділяємо очікування на мілісекунди та мікросекунди для стабільності ядра
    uint32_t delay_ms = current_delay_us / 1000;
    uint32_t remainder_us = current_delay_us % 1000;
    
    delay(delay_ms);                 // Віддаємо процесорний час системі на N мілісекунд
    delayMicroseconds(remainder_us); // Добиваємо мікросекундну точність

    // 3. Ін'єкція пакета в радіоефір
    transmit_spoofed_beacon(TARGET_UAV_01);
}
