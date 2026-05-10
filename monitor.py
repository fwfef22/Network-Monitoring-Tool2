import os
import platform
import time
import csv
from datetime import datetime

# Пытаемся импортировать библиотеки для графиков, если они установлены
try:
    import pandas as pd
    import matplotlib.pyplot as plt

    HAS_ANALYTICS = True
except ImportError:
    HAS_ANALYTICS = False

# --- КОНФИГУРАЦИЯ ---
HOSTS = {
    "MikroTik_Gateway": "192.168.88.1",
    "Google_DNS": "8.8.8.8",
    "Local_Host": "127.0.0.1"
}
REPORT_FILE = 'network_report.csv'
CHECK_INTERVAL = 2  # Пауза между проверками (сек)
SAMPLES = 10  # Сколько раз проверить перед выходом


# --- ФУНКЦИЯ ПИНГА ---
def ping_host(ip):
    # -n для Windows, -c для Linux/Mac
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = f"ping {param} 1 {ip}"

    start = time.time()
    # Выполняем и скрываем вывод консоли
    exit_code = os.system(command + " > nul 2>&1")
    end = time.time()

    latency = round((end - start) * 1000, 2)
    return exit_code == 0, latency


# --- ФУНКЦИЯ СОХРАНЕНИЯ В CSV ---
def log_to_csv(data):
    file_exists = os.path.isfile(REPORT_FILE)
    with open(REPORT_FILE, mode='a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Timestamp", "Host", "Status", "Latency (ms)"])
        writer.writerow(data)


# --- ФУНКЦИЯ ПОСТРОЕНИЯ ГРАФИКА ---
def generate_chart():
    if not HAS_ANALYTICS:
        print("\n[!] Для графиков установи: pip install pandas matplotlib")
        return

    print("\n[📈] Генерирую график стабильности...")
    df = pd.read_csv(REPORT_FILE)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='mixed')

    plt.figure(figsize=(10, 5))
    for host in df['Host'].unique():
        subset = df[df['Host'] == host]
        plt.plot(subset['Timestamp'], subset['Latency (ms)'], marker='.', label=host)

    plt.title('Network Latency Analysis (MikroTik/External)')
    plt.xlabel('Time')
    plt.ylabel('Latency (ms)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    chart_name = "network_stability.png"
    plt.savefig(chart_name)
    print(f"[✅] График сохранен как {chart_name}")
    plt.show()


# --- ОСНОВНОЙ ЦИКЛ ---
def main():
    print(f"=== Мониторинг запущен ({platform.system()}) ===")

    try:
        for i in range(SAMPLES):
            print(f"\nПроверка {i + 1}/{SAMPLES}...")
            for name, ip in HOSTS.items():
                is_up, latency = ping_host(ip)
                status = "UP" if is_up else "DOWN"
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Логируем
                log_to_csv([timestamp, name, status, latency])

                # Красивый вывод в консоль
                color = "\033[92m" if is_up else "\033[91m"
                reset = "\033[0m"
                print(f"  {name:18} | {color}{status:4}{reset} | {latency} ms")

            time.sleep(CHECK_INTERVAL)

        print("\n=== Сбор данных окончен ===")
        generate_chart()

    except KeyboardInterrupt:
        print("\nМониторинг остановлен пользователем.")


if __name__ == "__main__":
    main()