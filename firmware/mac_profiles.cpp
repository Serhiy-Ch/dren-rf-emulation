/*
 * D.R.E.N. - Distributed RF Emulation Network
 * Module: UAV Signature Database (Implementation)
 * Description: Storage for specific drone profiles.
 */

#include "mac_profiles.h"

// Фактичне виділення пам'яті та ініціалізація нашої цілі з OSINT
const UAVSignature TARGET_UAV_01 = {
    {0x84, 0xCC, 0xA8, 0x60, 0x43, 0x24}, // Target MAC
    "GBR-OP-123ABCD",                       // Target SSID
    1,                                      // Channel (базовий для Beacon)
    "Standard Industrial UAV"               // Vendor info
};
