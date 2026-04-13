#!/usr/bin/env python3
"""
D.R.E.N. - Distributed RF Emulation Network
Module: 802.11 Beacon Sniffer & Pcap Analyzer
"""

from scapy.all import sniff
from scapy.layers.dot11 import Dot11, Dot11Beacon, Dot11Elt, RadioTap
import argparse
import time

def analyze_beacon(pkt):
    """
    Обробляє пакет: витягує MAC, RSSI та SSID з Beacon-кадрів.
    """
    if pkt.haslayer(Dot11Beacon):
        bssid = pkt[Dot11].addr2
        
        try:
            ssid = pkt[Dot11Elt].info.decode('utf-8')
        except UnicodeDecodeError:
            ssid = "<Hidden or Corrupted>"
        
        rssi = -100 # За замовчуванням
        if pkt.haslayer(RadioTap):
            try:
                rssi = pkt[RadioTap].dBm_AntSignal
            except AttributeError:
                pass
        
        # Форматуємо вивід
        print(f"[*] MAC: {bssid} | RSSI: {rssi} dBm | SSID: {ssid}")

def main():
    # Налаштовуємо аргументи командного рядка (Think Outside The Box!)
    parser = argparse.ArgumentParser(description="D.R.E.N. Beacon Analyzer")
    parser.add_argument("-i", "--interface", help="Інтерфейс для Live Sniffing (наприклад, wlan0mon)")
    parser.add_argument("-r", "--read", help="Шлях до файлу .pcap для офлайн аналізу")
    args = parser.parse_args()

    if args.read:
        print(f"[+] Режим аналізу файлу: читання {args.read} ...\n")
        try:
            # Читаємо пакети з файлу
            sniff(offline=args.read, prn=analyze_beacon, store=False)
            print("\n[+] Аналіз файлу завершено.")
        except FileNotFoundError:
            print(f"[!] Помилка: Файл {args.read} не знайдено.")
    
    elif args.interface:
        print(f"[+] Режим Live Sniffing: прослуховування інтерфейсу {args.interface} ...")
        print("[+] Очікування 802.11 Beacon кадрів. Натисніть Ctrl+C для зупинки.\n")
        try:
            sniff(iface=args.interface, prn=analyze_beacon, store=False)
        except Exception as e:
            print(f"[!] Виникла помилка: {e}")
    else:
        print("[!] Вкажіть джерело даних. Використовуйте -h для допомоги.")
        print("Приклад 1: python packet_sniffer.py -i wlan0mon")
        print("Приклад 2: python packet_sniffer.py -r drone_traffic.pcap")

if __name__ == "__main__":
    main()
