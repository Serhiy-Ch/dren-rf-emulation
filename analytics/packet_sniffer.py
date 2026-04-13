#!/usr/bin/env python3
"""
D.R.E.N. - Distributed RF Emulation Network
Module: 802.11 Beacon Analyzer & Data Pipeline
Version: 2.0 (Structured Data & Metrics Extraction)
"""

from scapy.all import sniff
from scapy.layers.dot11 import Dot11, Dot11Beacon, Dot11Elt, RadioTap
import argparse
import time
import csv
import sys
import os

# Словник для відстеження часу останнього пакету для кожного MAC (для розрахунку Jitter)
last_seen_mac = {}

def analyze_beacon(pkt, csv_writer):
    """
    Обробляє пакет: витягує метрики (MAC, RSSI, Sequence, Jitter, IE) та записує у CSV.
    """
    if not pkt.haslayer(Dot11Beacon):
        return

    # 1. Базові ідентифікатори
    bssid = pkt[Dot11].addr2
    
    # 2. Sequence Number (Порядковий номер). У Scapy він зсунутий на 4 біти вправо.
    try:
        seq_num = pkt[Dot11].SC >> 4
    except AttributeError:
        seq_num = -1

    # 3. Надійне витягання SSID (обробка порожніх або битих IE)
    try:
        ssid = pkt[Dot11Elt].info.decode('utf-8') if pkt[Dot11Elt].info else "<Empty>"
    except Exception:
        ssid = "<Corrupted>"

    # 4. RSSI (Потужність сигналу) з перевіркою наявності поля
    rssi = ""
    if pkt.haslayer(RadioTap):
        try:
            rssi = pkt[RadioTap].dBm_AntSignal
        except AttributeError:
            pass # Драйвер не передав RSSI

    # 5. Розрахунок Jitter (Дельта часу між пакетами одного MAC)
    current_time = time.time()
    jitter = ""
    if bssid in last_seen_mac:
        jitter = round(current_time - last_seen_mac[bssid], 6)
    last_seen_mac[bssid] = current_time

    # Форматуємо час для логу
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_time))

    # Вивід у консоль для візуального контролю
    print(f"[{timestamp}] MAC: {bssid} | Seq: {seq_num} | RSSI: {rssi} | Jitter: {jitter}s | SSID: {ssid}")

    # Запис рядка у CSV файл
    if csv_writer:
        csv_writer.writerow([timestamp, bssid, ssid, rssi, seq_num, jitter])

def main():
    parser = argparse.ArgumentParser(description="D.R.E.N. Structured Data Pipeline")
    parser.add_argument("-i", "--interface", help="Інтерфейс для Live Sniffing (напр. wlan0mon)")
    parser.add_argument("-r", "--read", help="Шлях до файлу .pcap для офлайн аналізу")
    parser.add_argument("-o", "--output", default="dren_capture.csv", help="Файл для збереження результатів (CSV)")
    
    args = parser.parse_args()

    if not args.interface and not args.read:
        print("[!] Помилка: Вкажіть джерело даних (-i або -r).")
        sys.exit(1)

    print(f"[*] Ініціалізація D.R.E.N. Pipeline...")
    print(f"[*] Дані будуть збережені у файл: {args.output}\n")

    # Відкриваємо CSV файл для запису
    file_mode = 'a' if os.path.exists(args.output) else 'w'
    with open(args.output, mode=file_mode, newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        
        # Записуємо заголовки, якщо файл новий
        if file_mode == 'w':
            csv_writer.writerow(['Timestamp', 'BSSID', 'SSID', 'RSSI_dBm', 'Sequence_Num', 'Jitter_sec'])

        # Створюємо callback-функцію, яка вже містить наш csv_writer
        def packet_handler(pkt):
            analyze_beacon(pkt, csv_writer)

        try:
            if args.read:
                print(f"[+] Читання файлу {args.read} ...")
                # Читаємо файл без фільтрів, бо pcap вже зібраний
                sniff(offline=args.read, prn=packet_handler, store=False)
                print("[+] Офлайн аналіз завершено.")
                
            elif args.interface:
                print(f"[+] Прослуховування інтерфейсу {args.interface} ... (Ctrl+C для зупинки)")
                # ОПТИМІЗАЦІЯ: filter="type mgt subtype beacon" змушує Scapy відкидати весь зайвий трафік ще на рівні ядра
                sniff(iface=args.interface, filter="type mgt subtype beacon", prn=packet_handler, store=False)
                
        except KeyboardInterrupt:
            print("\n[*] Зупинка перехоплення користувачем.")
        except Exception as e:
            print(f"\n[!] Критична помилка: {e}")

if __name__ == "__main__":
    main()
