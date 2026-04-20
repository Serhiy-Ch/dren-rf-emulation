/*
 * D.R.E.N. - Distributed RF Emulation Network
 * Module: MAC Address & SSID Profile Database
 * Description: Defines vendor-specific OUIs and device signatures 
 * for realistic multi-node emulation.
 */

#ifndef MAC_PROFILES_H
#define MAC_PROFILES_H

#include <Arduino.h>

// Структура для зберігання повного профілю дрона
struct DroneProfile {
    uint8_t mac[6];      // 48-бітний MAC-адрес
    const char* ssid;    // Назва точки доступу (якщо є)
    const char* vendor;  // Назва виробника для логів
};

// --- ОСНОВНІ ПРОФІЛІ (Отримані під час аналізу) ---

// Профіль 1: Цільовий дрон з нашої OSINT-розвідки
const DroneProfile TARGET_UAV_01 = {
    {0x84, 0xCC, 0xA8, 0x60, 0x43, 0x24}, 
    "GBR-OP-123ABCD", 
    "Standard Industrial UAV"
};

// Профіль 2: Шаблон для масової імітації (Randomized OUI)
const uint8_t GENERIC_VENDOR_OUI[3] = {0x60, 0x60, 0x1F}; 

#endif

