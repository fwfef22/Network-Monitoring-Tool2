import os
import platform
import time
import csv
from datetime import datetime

try:
    import pandas as pd
    import matplotlib.pyplot as plt
    HAS_ANALYTICS = True
except ImportError:
    HAS_ANALYTICS = False

HOSTS = {
    "Brama_MikroTik": "192.168.88.1",
    "Google_DNS": "8.8.8.8",
    "Local_Host": "127.0.0.1"
}
REPORT_FILE = 'raport_sieciowy.csv'
CHECK_INTERVAL = 2  
SAMPLES = 10 


def ping_host(ip):
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = f"ping {param} 1 {ip}"

    start = time.time()
    exit_code = os.system(command + " > nul 2>&1" if platform.system().lower() == 'windows' else command + " > /dev/null 2>&1")
    end = time.time()

    latency = round((end - start) * 1000, 2)
    return exit_code == 0, latency


def log_to_csv(data):
    file_exists = os.path.isfile(REPORT_FILE)
    with open(REPORT_FILE, mode='a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Znacznik_czasu", "Host", "Status", "Opoznienie (ms)"])
        writer.writerow(data)


def generate_chart():
    if not HAS_ANALYTICS:
        print("\n[!] Aby wygenerować wykresy, zainstaluj: pip install pandas matplotlib")
        return

    print("\n[📈] Generowanie wykresu stabilności...")
    df = pd.read_csv(REPORT_FILE)
    df['Znacznik_czasu'] = pd.to_datetime(df['Znacznik_czasu'], format='mixed')

    plt.figure(figsize=(10, 5))
    for host in df['Host'].unique():
        subset = df[df['Host'] == host]
        plt.plot(subset['Znacznik_czasu'], subset['Opoznienie (ms)'], marker='.', label=host)

    plt.title('Analiza opóźnień sieciowych (MikroTik/Zewnętrzne)')
    plt.xlabel('Czas')
    plt.ylabel('Opóźnienie (ms)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    chart_name = "stabilnosc_sieci.png"
    plt.savefig(chart_name)
    print(f"[✅] Wykres zapisany jako {chart_name}")
    plt.show()


def main():
    print(f"=== Monitorowanie uruchomione ({platform.system()}) ===")

    try:
        for i in range(SAMPLES):
            print(f"\nPróba {i + 1}/{SAMPLES}...")
            for name, ip in HOSTS.items():
                is_up, latency = ping_host(ip)
                status = "OK" if is_up else "AWARIA"
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                log_to_csv([timestamp, name, status, latency])

                color = "\033[92m" if is_up else "\033[91m"
                reset = "\033[0m"
                print(f"  {name:18} | {color}{status:6}{reset} | {latency} ms")

            time.sleep(CHECK_INTERVAL)

        print("\n=== Zbieranie danych zakończone ===")
        generate_chart()

    except KeyboardInterrupt:
        print("\nMonitorowanie zatrzymane przez użytkownika.")


if __name__ == "__main__":
    main()
