#!/usr/bin/env python3
import os
import time
import random
import threading
import logging
import sqlite3
import datetime
import itertools
import sys
import requests
from scapy.all import sniff, ARP, ICMP

# ANSI color codes for colored output
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
RESET = "\033[0m"

# Configuration
DEFAULT_PORTS = [22, 21, 80, 443, 3389, 445, 1433, 3306, 25, 8080]
LOG_FILE = "honeypot.log"
DB_FILE = "honeypot_attacks.db"
ENABLE_IPTABLES_BAN = True  
ENABLE_TELEGRAM_ALERTS = False  # Enable if you wish to send Telegram alerts
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"
FAKE_OS = "Windows Server 2019 Datacenter"
RUNNING = True  # Control spinner animation

# (Fake banners removed since Fake Services option is deleted)

# Setup logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Initialize SQLite database to log events
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS attacks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT,
            port INTEGER,
            timestamp TEXT
        )"""
    )
    conn.commit()
    conn.close()
    print(f"{GREEN}[+] Database initialized.{RESET}")

# Change MAC address (MAC Spoofing)
def change_mac(interface="eth0"):
    new_mac = "02:%02x:%02x:%02x:%02x:%02x" % tuple(random.randint(0, 255) for _ in range(5))
    os.system(f"ifconfig {interface} down")
    os.system(f"ifconfig {interface} hw ether {new_mac}")
    os.system(f"ifconfig {interface} up")
    print(f"{GREEN}[+] MAC Address changed to {new_mac}.{RESET}")

# Modify TTL value
def modify_ttl(value=64):
    os.system(f"sysctl -w net.ipv4.ip_default_ttl={value}")
    print(f"{GREEN}[+] TTL set to {value}.{RESET}")

# Disable ICMP (Block Ping)
def disable_icmp():
    os.system("iptables -A INPUT -p icmp --icmp-type echo-request -j DROP")
    print(f"{GREEN}[+] ICMP (ping) requests blocked.{RESET}")

# Reset settings to default (Basic)
def reset_defaults():
    os.system("ifconfig eth0 down")
    os.system("ifconfig eth0 hw ether 00:11:22:33:44:55")
    os.system("ifconfig eth0 up")
    os.system("sysctl -w net.ipv4.ip_default_ttl=64")
    os.system("iptables -D INPUT -p icmp --icmp-type echo-request -j DROP")
    os.system("service tor stop")
    os.system("killall openvpn")
    print(f"{YELLOW}[+] Settings reset to default.{RESET}")

# Intrusion Detection using scapy
def intrusion_detection():
    def packet_callback(packet):
        if packet.haslayer(ICMP) or packet.haslayer(ARP):
            print(f"{RED}[!] Suspicious network activity detected: {packet.summary()}{RESET}")
    print(f"{GREEN}[+] Intrusion detection enabled. Monitoring network...{RESET}")
    sniff(store=False, prn=packet_callback)

# Hide process (Anti-Detection)
def hide_process():
    # ملاحظة: هذا مثال مبسط؛ إخفاء العملية فعليًا قد يتطلب تقنيات متقدمة خاصة بالنظام
    os.system("echo '0' > /proc/sys/kernel/yama/ptrace_scope")
    print(f"{GREEN}[+] Process hiding enabled.{RESET}")

# Auto-change settings periodically (Auto-Spoofing)
def auto_change(interval=300):
    print(f"{GREEN}[+] Auto-change enabled. Settings will change every {interval} seconds.{RESET}")
    while True:
        change_mac()
        modify_ttl(random.randint(50, 128))
        time.sleep(interval)

# Animated spinner for visual status
def spinner():
    global RUNNING
    spinner_cycle = itertools.cycle(["|", "/", "-", "\\"])
    while RUNNING:
        sys.stdout.write(f"\r{CYAN}🌀 Tool running... {next(spinner_cycle)} {RESET}")
        sys.stdout.flush()
        time.sleep(0.2)
    sys.stdout.write(f"\r{GREEN}✅ Tool stopped!{RESET}\n")

# Main menu with color-coded options and reordered choices
def menu():
    while True:
        print(f"""{MAGENTA}
Select the features you want to enable:
[1] Change MAC Address
[2] Modify TTL
[3] Disable ICMP (Block Ping)
[4] Enable All (Change MAC, Modify TTL, Disable ICMP)
[5] Stealth Mode (Auto-Hide: Change MAC, Modify TTL, Disable ICMP)
[6] Enable Intrusion Detection
[7] Hide Process (Anti-Detection)
[8] Enable Auto-Change (Periodic Spoofing)
[9] Reset to Default
[10] Exit
{RESET}""")
        choice = input(f"{YELLOW}Enter your choice (e.g., 1,2 for multiple selections): {RESET}")
        if "1" in choice:
            change_mac()
        if "2" in choice:
            modify_ttl()
        if "3" in choice:
            disable_icmp()
        if "4" in choice:
            change_mac()
            modify_ttl()
            disable_icmp()
        if "5" in choice:
            change_mac()
            modify_ttl()
            disable_icmp()
            print(f"{GREEN}[+] Stealth mode activated.{RESET}")
        if "6" in choice:
            threading.Thread(target=intrusion_detection, daemon=True).start()
        if "7" in choice:
            hide_process()
        if "8" in choice:
            threading.Thread(target=auto_change, daemon=True).start()
        if "9" in choice:
            reset_defaults()
        if "10" in choice:
            break

if __name__ == "__main__":
    init_db()
    threading.Thread(target=spinner, daemon=True).start()  # تشغيل السبينر في الخلفية
    menu()
