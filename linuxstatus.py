#!/usr/bin/env python3

import json
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime

# --- Alunos devem implementar as funções abaixo --- #

#status

def get_datetime():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_uptime():
    # pegar diretamente de /proc/uptime
    # converter pra seconds
    f = open("/proc/uptime", "r")
    print(f.read()) 

    return 0  # TODO

# /proc/cpuinfo
# carregar arquivo e formatar para JSOn
def get_cpu_info():
    return {
        "model": "TODO",
        "speed_mhz": 0,
        "usage_percent": 0.0
    }

# /proc/meminfo
def get_memory_info():
    return {
        "total_mb": 0,
        "used_mb": 0
    }

# /proc/version
def get_os_version():
    return "TODO"

# /proc
def get_process_list():
    return []  # lista de { "pid": int, "name": str }
# /proc/diskstats
def get_disks():
    return []  # lista de { "device": str, "size_mb": int }
# /proc/devices
def get_usb_devices():
    return []  # lista de { "port": str, "description": str }
# /proc/net/ alguma coisa
def get_network_adapters():
    return []  # lista de { "interface": str, "ip_address": str }

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