
/*
 * D.R.E.N. - Distributed RF Emulation Network
 * Module: Stochastic Interval Generator
 * Description: Calculates timing intervals for beacon transmission
 * using hardware RNG and bounded multiplier logic.
 */

#include <Arduino.h>

// ================= CONFIGURATION =================
const uint32_t BASE_INTERVAL_US = 400000; // 400 ms base interval

// Multiplier thresholds (моделювання пропущених базових подій)
const uint8_t PROB_MULTIPLIER_X3 = 5;  // 5% chance: wait 3x base interval
const uint8_t PROB_MULTIPLIER_X2 = 15; // 15% chance: wait 2x base interval
// Remaining 80% will use 1x base interval

// Jitter boundaries 
// (Зміщення в плюс, оскільки апаратні затримки процесора зазвичай додають час, а не віднімають його)
const int32_t JITTER_MIN_US = -1000; 
const int32_t JITTER_MAX_US = 12000;

// Safety boundaries логічно прив'язані до базового інтервалу
const uint32_t MIN_INTERVAL_US  = BASE_INTERVAL_US / 2; // 200 ms
const uint32_t MAX_INTERVAL_US  = BASE_INTERVAL_US * 4; // 1.6 s
// =================================================

// Compile-time safety check
static_assert(BASE_INTERVAL_US > 0, "Base interval must be positive");

// Ініціалізація з використанням апаратного TRNG. 
// Параметр deterministic дозволяє фіксувати seed для тестів.
void setup_jitter_engine(bool deterministic = false) {
    if (deterministic) {
        randomSeed(42); // Фіксована послідовність для лабораторної перевірки
    } else {
        randomSeed(esp_random()); // Апаратний генератор ESP32
    }
}

// Calculates a microsecond jitter deviation
int32_t generate_microsecond_jitter() {
    return random(JITTER_MIN_US, JITTER_MAX_US + 1);
}

// Calculates the base interval multiplier
uint8_t calculate_interval_multiplier() {
    uint8_t chance = random(1, 101); 
    
    if (chance <= PROB_MULTIPLIER_X3) {
        return 3; 
    } else if (chance <= (PROB_MULTIPLIER_X3 + PROB_MULTIPLIER_X2)) {
        return 2; 
    } else {
        return 1; 
    }
}

// Main function: Calculates and returns the final delay in microseconds
uint32_t get_next_delay_us() {
    uint8_t multiplier = calculate_interval_multiplier();
    int32_t jitter = generate_microsecond_jitter();
    
    // Explicit int32_t casting prevents overflow before applying bounds
    int32_t total_delay = ((int32_t)BASE_INTERVAL_US * multiplier) + jitter;
    
    // Strict bounds enforcement
    if (total_delay < (int32_t)MIN_INTERVAL_US) {
        return MIN_INTERVAL_US;
    } else if (total_delay > (int32_t)MAX_INTERVAL_US) {
        return MAX_INTERVAL_US;
    }
    
    return (uint32_t)total_delay;
}
