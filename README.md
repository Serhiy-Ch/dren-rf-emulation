# dren-rf-emulation
RF Deception &amp; Signal Environment Simulation Framework using distributed ESP32/ESP8266 nodes
# 📡 D.R.E.N. (Distributed RF Emulation Network)
### RF Deception & Signal Environment Simulation Framework

> **⚠️ Disclaimer:** This project is intended exclusively for research, educational, and defensive cybersecurity purposes.

## 📌 Project Overview
D.R.E.N. is a research framework in the field of RF engineering and cybersecurity, designed to generate controlled RF noise and synthetic 802.11 network entities in the 2.4 GHz band.

The system applies a **"Think Outside The Box!"** approach, shifting away from expensive SDR hardware. Instead, it leverages the core principle of **"divide and separate"**: using a distributed array of low-cost hardware nodes (ESP32/ESP8266) to create a highly realistic, stochastic signal environment.

## 🏗️ Architecture
* **Layer 1 — Hardware Nodes:** ESP32/ESP8266 microcontrollers with autonomous power.
* **Layer 2 — Signal Engine:** Direct 802.11 Beacon frame generation with dynamic MAC/OUI profiles.
* **Layer 3 — Behavior Engine:** Stochastic timing models (mathematical jitter) and channel hopping.
* **Layer 4 — Coordination:** Node synchronization for complex scenarios ("cluster deployment", "convoy movement").
* **Layer 5 — Analytics:** Python/Scapy pipeline to analyze RSSI variance, Jitter, and Sequence patterns.

## 🔬 Research Questions
1. Is it possible to distinguish synthetic RF entities from real ones using standard DPI?
2. Which detection metrics are most reliable: RSSI variance or hardware clock skew?
3. How does mathematical jitter influence the detection rate?

---

## 🇺🇦 Опис проєкту (Українською)
D.R.E.N. — це дослідницький фреймворк для створення контрольованого RF-шуму та синтетичних мережевих сутностей 802.11. Система використовує принцип розподілених вузлів для створення максимально реалістичного сигнального середовища, досліджуючи стійкість алгоритмів SIGINT та DPI до маніпуляцій.

## 📂 Repository Structure
* `firmware/` — С++ code for microcontrollers.
* `analytics/` — Python scripts for signal analysis and visualization.

## 🔬 Phase 1: Baseline Traffic Analysis
Built a Python-based RF data analysis pipeline using Pandas and Matplotlib to visualize signal stability and timing behavior from captured 802.11 beacon metadata.

**1. Data Collection & Cleaning:**
Traffic was parsed using our Python pipeline, extracting precise timestamps, RSSI values, and Jitter metrics into a structured CSV format. Missing values and initial zero-jitter anomalies were automatically filtered out.

**2. Key Observations:**
* **Signal Stability:** The RSSI remained highly stable (-31 to -35 dBm), indicating a clean capture environment.
* **Timing Fingerprint (Jitter):** The beacon interval is not a standard 100ms. The device exhibits a quantized transmission pattern with a strict base interval of **~400ms**. Spikes in jitter indicate normal packet loss perfectly correlated with the 400ms base multiplier.

**3. Engineering Conclusion:**
To successfully emulate this UAV profile, the ESP32 firmware must not only spoof the MAC and SSID but strictly adhere to a 400ms beacon interval while introducing stochastic micro-delays to mimic real hardware processing behavior.
