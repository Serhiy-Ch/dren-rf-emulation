
/*
 * D.R.E.N. - Distributed RF Emulation Network
 * Module: Stochastic Interval Generator for Lab Traffic Simulation
 * Description: Generates quantized intervals with true microsecond precision
 * and stochastic packet loss emulation based on real-world baselines.
 * * Expected Output Range: ~396,000 us to ~1,212,000 us
 * Expected Distribution: 80% @ 1x Base, 15% @ 2x Base, 5% @ 3x Base (+/- Jitter)
 */

#include <Arduino.h>

// ================= CONFIGURATION =================
const uint32_t BASE_INTERVAL_US = 400000; // 400 ms in microseconds

// Safety boundaries
const uint32_t MIN_INTERVAL_US  = 100000;  // Absolute lower bound (100 ms)
const uint32_t MAX_INTERVAL_US  = 1500000; // Absolute upper bound (1.5 s)

// Jitter boundaries (microsecond deviations)
const int32_t JITTER_MIN_US = -4000;
const int32_t JITTER_MAX_US = 12000;

// Probability thresholds for simulated packet loss (%)
const uint8_t PROB_DOUBLE_LOSS = 5;  // 5% chance to lose 2 packets
const uint8_t PROB_SINGLE_LOSS = 15; // 15% chance to lose 1 packet
// =================================================

// Compile-time safety check
static_assert(BASE_INTERVAL_US > 0, "Base interval must be positive");

// Initializes the random number generator using atmospheric noise and execution time
void setup_jitter_engine() {
    randomSeed(analogRead(A0) ^ micros()); 
}

// Generates a true microsecond jitter within defined boundaries
int32_t generate_microsecond_jitter() {
    return random(JITTER_MIN_US, JITTER_MAX_US + 1);
}

// Emulates packet loss by returning a time multiplier
uint8_t calculate_packet_loss_multiplier() {
    uint8_t chance = random(1, 101); 
    
    if (chance <= PROB_DOUBLE_LOSS) {
        return 3; 
    } else if (chance <= (PROB_DOUBLE_LOSS + PROB_SINGLE_LOSS)) {
        return 2; 
    } else {
        return 1; 
    }
}

// Main function: Calculates and returns the final delay in microseconds
uint32_t get_next_delay_us() {
    uint8_t multiplier = calculate_packet_loss_multiplier();
    int32_t jitter = generate_microsecond_jitter();
    
    int32_t total_delay = ((int32_t)BASE_INTERVAL_US * multiplier) + jitter;
    
    // Strict bounds enforcement
    if (total_delay < (int32_t)MIN_INTERVAL_US) {
        return MIN_INTERVAL_US;
    } else if (total_delay > (int32_t)MAX_INTERVAL_US) {
        return MAX_INTERVAL_US;
    }
    
    return (uint32_t)total_delay;
}
