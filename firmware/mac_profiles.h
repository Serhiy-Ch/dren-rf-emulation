
/*
 * D.R.E.N. - Distributed RF Emulation Network
 * Module: UAV Signature Database (Header)
 * Description: Defines the formal contract for drone radio signatures.
 */

#ifndef MAC_PROFILES_H
#define MAC_PROFILES_H

#include <Arduino.h>

// Формалізований контракт: ssid може бути nullptr (для прихованих мереж)
struct UAVSignature {
    uint8_t mac[6];
    const char* ssid;     // Може бути nullptr
    uint8_t channel;      // Wi-Fi канал для точної ін'єкції
    const char* vendor;   // Для внутрішнього логування
};

// Оголошуємо наявність профілю, але НЕ виділяємо під нього пам'ять тут
extern const UAVSignature TARGET_UAV_01;

#endif

