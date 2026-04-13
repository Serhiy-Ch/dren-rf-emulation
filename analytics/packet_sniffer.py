#!/usr/bin/env python3
"""
D.R.E.N. - Distributed RF Emulation Network
Module: 802.11 Beacon Analyzer & Data Pipeline
Version: 4.0 (OOP Architecture, Type Safety, Deep Summary)
"""

from scapy.all import sniff
from scapy.layers.dot11 import Dot11, Dot11Beacon, Dot11Elt, RadioTap
import argparse
import time
import csv
import sys
import os

class BeaconAnalyzer:
    def __init__(self, output_file):
        """Ініціалізація аналізатора, відкриття файлу та створення лічильників."""
        self.output_file = output_file
        self.last_seen_mac = {}
        self.mac_stats = {}  # Зберігає агреговані дані: кількість, сума джитера, сума довжини
        
        # Глобальні лічильники якості даних
        self.total_packets = 0
        self.empty_ssid_count = 0
        self.no_rssi_count = 0
        
        # Налаштування CSV
        file_mode = 'a' if os.path.exists(output_file) else 'w'
        self.file = open(output_file, mode=file_mode, newline='', encoding='utf-8')
        self.csv_writer = csv.writer(self.file)
        
        if file_mode == 'w':
            self.csv_writer.writerow(['Timestamp_Epoch', 'BSSID', 'SSID', 'RSSI_dBm', 'Sequence_Num', 'Frame_Length', 'Jitter_sec'])

    def __del__(self):
        """Безпечне закриття файлу при завершенні роботи."""
        if hasattr(self, 'file') and self.file:
            self.file.close()

    def extract_fields(self, pkt):
        """Ізольована логіка витягання даних із пакета."""
        bssid = pkt[Dot11].addr2
        current_time = float(pkt.time)
        frame_len = len(pkt)

        try:
            seq_num = pkt[Dot11].SC >> 4
        except AttributeError:
            seq_num = -1

        ssid = ""
        try:
            ssid_layer = pkt.getlayer(Dot11Elt, ID=0)
            if ssid_layer and ssid_layer.info:
                ssid = ssid_layer.info.decode('utf-8', errors='ignore')
        except Exception:
            ssid = "<Corrupted>"

        rssi = None
        if pkt.haslayer(RadioTap):
            try:
                rssi = pkt[RadioTap].dBm_AntSignal
            except AttributeError:
                pass

        return current_time, bssid, ssid, rssi, seq_num, frame_len

    def process_packet(self, pkt):
        """Головний метод обробки: агрегація, розрахунки та запис."""
        if not pkt.haslayer(Dot11Beacon):
            return

        current_time, bssid, ssid, rssi, seq_num, frame_len = self.extract_fields(pkt)

        # Оновлення лічильників якості даних
        self.total_packets += 1
        if not ssid:
            self.empty_ssid_count += 1
            ssid = "<Empty>"
        if rssi is None:
            self.no_rssi_count += 1

        # Розрахунок Jitter (тепер строго float)
        jitter = 0.0
        if bssid in self.last_seen_mac:
            jitter = current_time - self.last_seen_mac[bssid]
        self.last_seen_mac[bssid] = current_time

        # Оновлення статистики для конкретного MAC
        if bssid not in self.mac_stats:
            self.mac_stats[bssid] = {'count': 0, 'jitter_sum': 0.0, 'frame_len_sum': 0}
        self.mac_stats[bssid]['count'] += 1
        self.mac_stats[bssid]['jitter_sum'] += jitter
        self.mac_stats[bssid]['frame_len_sum'] += frame_len

        # Вивід у консоль
        timestamp_str = time.strftime('%H:%M:%S', time.localtime(current_time))
        rssi_str = str(rssi) if rssi is not None else "None"
        print(f"[{timestamp_str}] MAC: {bssid} | Seq: {seq_num} | RSSI: {rssi_str} | Len: {frame_len} | Jitter: {jitter:.6f}s | SSID: {ssid}")

        # Запис у CSV
        self.csv_writer.writerow([current_time, bssid, ssid, rssi, seq_num, frame_len, round(jitter, 6)])
        
        # Оптимізація I/O: скидаємо буфер на диск кожні 50 пакетів
        if self.total_packets % 50 == 0:
            self.file.flush()

    def print_summary(self):
        """Генерація фінального інженерного звіту."""
        self.file.flush()
        print("\n" + "="*55)
        print("D.R.E.N. CAPTURE & QUALITY SUMMARY")
        print("="*55)
        print(f"Загалом Beacon-кадрів: {self.total_packets}")
        print(f"Кадрів без RSSI: {self.no_rssi_count}")
        print(f"Кадрів з порожнім SSID: {self.empty_ssid_count}")
        print(f"Унікальних BSSID (пристроїв): {len(self.mac_stats)}")
        print("\nТоп-5 найактивніших пристроїв:")
        
        # Виправлене та безпечне сортування
        sorted_macs = sorted(self.mac_stats.items(), key=lambda x: x[1]['count'], reverse=True)[:5]
        
        for mac, stats in sorted_macs:
            count = stats['count']
            avg_jitter = stats['jitter_sum'] / count if count > 0 else 0
            avg_len = stats['frame_len_sum'] / count if count > 0 else 0
            print(f" - {mac}: {count} кадрів | Сер. Jitter: {avg_jitter:.6f}s | Сер. Довжина: {avg_len:.0f} b")
        print("="*55 + "\n")

def main():
    parser = argparse.ArgumentParser(description="D.R.E.N. Structured Data Pipeline")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-i", "--interface", help="Інтерфейс для Live Sniffing (напр. wlan0mon)")
    group.add_argument("-r", "--read", help="Шлях до файлу .pcap для офлайн аналізу")
    parser.add_argument("-o", "--output", default="dren_capture.csv", help="Файл результатів (CSV)")
    
    args = parser.parse_args()

    print(f"[*] Ініціалізація D.R.E.N. Pipeline v4.0 (OOP Architecture)...")
    print(f"[*] Дані будуть збережені у файл: {args.output}\n")

    # Створюємо екземпляр нашого аналізатора
    analyzer = BeaconAnalyzer(args.output)

    try:
        if args.read:
            print(f"[+] Читання файлу {args.read} ...")
            sniff(offline=args.read, prn=analyzer.process_packet, store=False)
        elif args.interface:
            print(f"[+] Прослуховування інтерфейсу {args.interface} ... (Ctrl+C для зупинки)")
            sniff(iface=args.interface, filter="type mgt subtype beacon", prn=analyzer.process_packet, store=False)
    except KeyboardInterrupt:
        print("\n[*] Зупинка перехоплення користувачем.")
    except Exception as e:
        print(f"\n[!] Критична помилка: {e}")
    finally:
        # Незалежно від того, як завершився скрипт (успіх чи Ctrl+C), показуємо звіт
        analyzer.print_summary()

if __name__ == "__main__":
    main()
