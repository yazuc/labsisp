#!/usr/bin/env python3

import json
import time
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime

# --- Alunos devem implementar as funções abaixo --- #

#status

def get_datetime():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_uptime():
    with open("/proc/uptime", "r") as f:
        uptime_seconds = float(f.readline().split()[0])
    return int(uptime_seconds)

# /proc/cpuinfo
# carregar arquivo e formatar para JSOn
def get_cpu_info():
    # Inicializa variáveis
    model = "Desconhecido"
    speed_mhz = 0

    # Lê /proc/cpuinfo
    with open("/proc/cpuinfo", "r") as f:
        for line in f:
            if "model name" in line and model == "Desconhecido":
                model = line.strip().split(":", 1)[1].strip()
            elif "cpu MHz" in line and speed_mhz == 0:
                speed_mhz = float(line.strip().split(":", 1)[1].strip())

    # Lê /proc/stat duas vezes para calcular uso da CPU
    def read_cpu_times():
        with open("/proc/stat", "r") as f:
            fields = f.readline().strip().split()[1:]
            fields = list(map(int, fields))
            idle = fields[3]  # idle
            total = sum(fields)
            return idle, total

    idle1, total1 = read_cpu_times()
    time.sleep(1)
    idle2, total2 = read_cpu_times()

    idle_delta = idle2 - idle1
    total_delta = total2 - total1
    usage_percent = 100.0 * (1.0 - idle_delta / total_delta) if total_delta != 0 else 0.0

    return {
        "model": model,
        "speed_mhz": speed_mhz,
        "usage_percent": round(usage_percent, 2)
    }

def get_memory_info():
    meminfo = {}

    with open("/proc/meminfo", "r") as f:
        for line in f:
            parts = line.split()
            key = parts[0].rstrip(":")
            value = int(parts[1])  # em KB
            meminfo[key] = value

    total_kb = meminfo.get("MemTotal", 0)
    free_kb = meminfo.get("MemFree", 0)
    buffers_kb = meminfo.get("Buffers", 0)
    cached_kb = meminfo.get("Cached", 0)

    used_kb = total_kb - free_kb - buffers_kb - cached_kb

    return {
        "total_mb": round(total_kb / 1024, 2),
        "used_mb": round(used_kb / 1024, 2)
    }

def get_os_version():
    with open('/proc/version', 'r') as f:
        return f.readline().strip()

# /proc
def get_process_list():
    processes = []
    for pid in os.listdir('/proc'):
        if pid.isdigit():
            try:
                with open(f'/proc/{pid}/comm', 'r') as f:
                    process_name = f.readline().strip()
                processes.append(({ "pid": pid, "name": process_name }))
            except IOError:
                continue
    return processes
# /proc/diskstats
def get_disks():
    with open('/proc/partitions', 'r') as f:
        disks = []
        for line in f.readlines()[2:]:
            parts = line.split()
            if len(parts) == 4:
                size_mb = int(parts[2]) // 1024
                name = parts[3]
                disks.append(({"device": name, "size_mb": size_mb}))
    return disks
# /proc/devices
def get_usb_devices():
    return []  # lista de { "port": str, "description": str }

# /proc/net/dev alguma coisa
def get_network_adapters():
    adapters = []
    with open("/proc/net/dev", "r") as f:
        lines = f.readlines()[2:]  # pula os cabeçalhos
        for line in lines:
            iface = line.split(":")[0].strip()
            #ip = get_ip_address(iface)
            #if ip:  # só adiciona interfaces com IP
            adapters.append({
                "interface": iface
                #"ip_address": ip
            })
    return adapters

# --- Servidor HTTP --- #

class StatusHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/status":
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")
            return

        response = {
            "datetime": get_datetime(),
            "uptime_seconds": get_uptime(),
            "cpu": get_cpu_info(),
            "memory": get_memory_info(),
            "os_version": get_os_version(),
            "processes": get_process_list(),
            "disks": get_disks(),
            "usb_devices": get_usb_devices(),
            "network_adapters": get_network_adapters()
        }

        data = json.dumps(response, indent=2).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

def run_server(port=8080):
    print(f"Servidor disponível em http://0.0.0.0:{port}/status")
    server = HTTPServer(("0.0.0.0", port), StatusHandler)
    server.serve_forever()

if __name__ == "__main__":
    run_server()
