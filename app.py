# -*- coding: UTF-8 -*-
# Internet Connection Monitor daemon- nelbren@nelbren.com @ 2025-02-14
import os
import time
import socket
import platform
from canvas import getStudents
from flask_socketio import SocketIO
from flask import Flask, render_template, request, jsonify

MY_VERSION = 1.5
ICM_VERSION = 4.4
DEBUG = 0

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", ssl_context=None)

# Diccionario para almacenar el estado de los clientes
clients_status = getStudents()  # {}


def get_status_row_color(last_update, status):
    elapsed = time.time() - last_update
    # print(elapsed)
    # print("STATUS ->", status)
    if status == "🌐":
        return "red", status

    if elapsed < 25:
        return "green", status
    elif elapsed < 40:
        return "yellow", status
    elif elapsed < 55:
        return "red", "⌛️"
    else:
        return "red", "❌"


def get_status_col_color(condition):
    return "green" if condition == "✔️" else "red"


def get_status_emoji(status):
    if status == "OK":
        return "✔️"
    if status == "INTERNET":
        return "🌐"
    return "❌"


def get_os_emoji(OS):
    if OS == "MACOS":
        return "🍎"
    elif OS == "LINUX":
        return "🐧"
    elif OS == "WINDOWS":
        return "🪟"
    elif OS == "RASPBERRY":
        return "🍓"
    return "⁉️"


def getOSM():
    OS = platform.system()
    if OS == "Linux":
        fileModel = '/proc/device-tree/model'
        if os.path.exists(fileModel):
            with open(fileModel) as f:
                model = f.read()
            if 'Raspberry' in model:
                OS = 'Raspberry'
    return OS.upper()


@app.route('/')
def index():
    server_ip = get_active_ipv4()
    # print(f"Server IP: {server_ip}")
    OS = getOSM()
    osEmoji = get_os_emoji(OS)
    return render_template('index.html', server_ip=server_ip, osEmoji=osEmoji,
                           MY_VERSION=MY_VERSION, ICM_VERSION=ICM_VERSION)


@app.route('/update', methods=['POST'])
def update():
    timestamp = time.time()
    data = request.json

    id = data.get("id", "")
    if id and id in clients_status:
        row = clients_status[id]["row"]
        name = clients_status[id]["name"]
        OS = data.get("OS", "N/A")
        OS = get_os_emoji(OS)
        icmVersion = data.get("icmVersion", "N/A")
        status = data.get("status", "N/A")
        # print(id, status, flush=True)
        status = get_status_emoji(status)
        # print(id, status, flush=True)
        # print(data, flush=True)
        ip = request.remote_addr
        elapsed = time.time() - timestamp
        color, status = get_status_row_color(time.time(), status)
        client_status = {
            "row": row,
            "name": name,
            "last_update": time.time(),
            "icmVersion": icmVersion,
            "OS": OS,
            "status": status,
            "ip": ip,
            "color": color,
            "ignored": False
        }
        ip_server = "127.0.0.1"
        if DEBUG:
            print(f"🔃➜💻{ip}🆔{id}➜🌐{ip_server}")
        # print("client_status ->", client_status)
        clients_status[id] = client_status

        data = {
                    "row": row,
                    "id": id,
                    "name": name,
                    "timestamp": timestamp,
                    "elapsed": elapsed,
                    "color": color,
                    "status": status,
                    "ip": ip,
                    "icmVersion": icmVersion,
                    "OS": OS
                }
        # print(f"{id} -> {data}", flush=True)

        socketio.emit('update_status', data)
        return jsonify({"message": "Updated successfully"}), 200
    else:
        print(f"❌🆔{id}❓UNKNOWN")
    return jsonify({"error": "Invalid data"}), 400


@socketio.on('request_status')
def send_status():
    """Envía el estado actualizado de los clientes con un índice de fila."""
    ok_count = 0
    warning_count = 0
    critical_count = 0
    ignore_count = 0
    active_count = 0
    # print(clients_status)
    for index, (id, info) in enumerate(clients_status.items(), start=1):
        # print("send_status - info ->", id, info)
        elapsed = time.time() - info["last_update"]
        status = info.get("status", "N/A")
        color, status = get_status_row_color(
            info["last_update"], status)
        ip = info.get("ip", "N/A")
        OS = info.get("OS", "N/A")
        icmVersion = info.get("icmVersion", "N/A")
        if DEBUG:
            print(f"🔃➜🌐➜💻{ip}🆔{id}")
        # print("request_status ->", ip)
        # print(id, info)
        ignored = info.get("ignored", False)
        if ignored:
            ignore_count += 1
        else:
            # print(id, "COLOR ->", color)
            active_count += 1
            if color == "green":
                ok_count += 1
            elif color == "yellow":
                warning_count += 1
            elif color == "red":
                critical_count += 1

        data = {
                    "row": index,
                    "id": id,
                    "name": info["name"],
                    "timestamp": info["last_update"],
                    "elapsed": elapsed,
                    "color": color,
                    "status": status,
                    "ip": ip,
                    "OS": OS,
                    "icmVersion": icmVersion
                }
        socketio.emit('update_status', data)
    # Emitir los contadores al frontend
    # print(ok_count, warning_count, critical_count)
    socketio.emit('update_counters', {
        "ok": ok_count,
        "warning": warning_count,
        "critical": critical_count,
        "ignore": ignore_count,
        "active": active_count
    })


@socketio.on('update_ignore_status')
def update_ignore_status(data):
    user_id = data.get("id")
    ignored = data.get("ignored")

    if user_id in clients_status:
        clients_status[user_id]["ignored"] = ignored

    # print('update_ignore_status', user_id, ignored)


def get_active_ipv4():
    try:
        # Crear un socket UDP y conectarse a un servidor público (Google DNS)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]  # Obtener la IP de la interfaz activa
    except Exception as e:
        print(f"Error obteniendo la IP: {e}")
        return "127.0.0.1"  # Retorno seguro en caso de fallo


@socketio.on('ping_server')
def handle_ping():
    """ Responde a los pings del frontend """
    socketio.emit('pong_client', {'timestamp': time.time()})


if __name__ == '__main__':
    socketio.run(app, debug=True)
