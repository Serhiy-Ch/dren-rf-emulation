import pandas as pd
import matplotlib.pyplot as plt
import os


def plot_dren_data(csv_file, base_interval=None):
    if not os.path.exists(csv_file):
        print(f"[!] Файл {csv_file} не знайдено.")
        return

    # 1. Читання та глибока очистка даних
    df = pd.read_csv(csv_file)
    df['RSSI_dBm'] = pd.to_numeric(df['RSSI_dBm'], errors='coerce')
    df['Jitter_sec'] = pd.to_numeric(df['Jitter_sec'], errors='coerce')

    # Відкидаємо биті рядки та нульовий стартовий jitter (щоб не спотворювати статистику)
    df = df.dropna(subset=['RSSI_dBm', 'Jitter_sec'])
    df = df[df['Jitter_sec'] > 0.0001]

    # Захист: перевірка, чи лишилися дані після очистки
    if df.empty:
        print("[!] Після очистки не залишилось валідних рядків.")
        return

    # Автоматичне визначення базового інтервалу (якщо не задано вручну)
    if base_interval is None:
        base_interval = df['Jitter_sec'].median()

    # 2. Аналітичний Summary у консоль
    print("\n" + "=" * 45)
    print("📈 D.R.E.N. ANALYTICAL SUMMARY")
    print("=" * 45)
    print(f"Total Packets Analyzed: {len(df)}")
    print(f"RSSI (Mean): {df['RSSI_dBm'].mean():.2f} dBm")
    print(f"RSSI (Std Dev): {df['RSSI_dBm'].std():.2f} dBm")
    print(f"Jitter (Mean): {df['Jitter_sec'].mean():.4f} s")
    print(f"Jitter (Median): {df['Jitter_sec'].median():.4f} s")
    print(f"Jitter (Max): {df['Jitter_sec'].max():.4f} s")
    print("=" * 45 + "\n")

    # 3. Побудова графіків
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

    # Графік RSSI
    ax1.plot(df.index, df['RSSI_dBm'], color='blue', marker='o', linestyle='-', linewidth=1, markersize=4)
    ax1.set_title('Signal Stability Analysis (RSSI over Time)', fontsize=14, fontweight='bold')
    ax1.set_ylabel('RSSI (dBm)', fontsize=12)
    ax1.set_xlabel('Packet Order', fontsize=12)
    ax1.grid(True, linestyle='--', alpha=0.7)

    # Графік Jitter
    ax2.bar(df.index, df['Jitter_sec'], color='orange', alpha=0.7)
    ax2.set_title('Timing Fingerprint Analysis (Jitter Distribution)', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Jitter (seconds)', fontsize=12)
    ax2.set_xlabel('Packet Order', fontsize=12)
    ax2.grid(True, axis='y', linestyle='--', alpha=0.7)

    # Лінія базового інтервалу
    ax2.axhline(y=base_interval, color='red', linestyle='--', label=f'Base Interval (~{base_interval:.2f}s)')
    ax2.legend()

    # Форматування та збереження у високій якості (dpi=200)
    plt.tight_layout()
    output_img = "dren_analysis_report.png"
    plt.savefig(output_img, dpi=200, bbox_inches="tight")
    print(f"[+] Графіки збережено у файл: {output_img}")

    plt.show()
    plt.close(fig)  # Охайне закриття процесу


if __name__ == "__main__":
    # Включаємо повністю автоматичний режим обчислення базового інтервалу
    plot_dren_data(r"C:\Users\User\PycharmProjects\D.R.E.N\dren_capture.csv", base_interval=None)