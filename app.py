# -*- coding: UTF-8 -*-
# Internet Connection Monitor daemon - nelbren@nelbren.com @ 2025-03-14
import os
import re
import time
import socket
import requests
import platform
import subprocess
from datetime import datetime, date
from canvas import getStudents
from flask_socketio import SocketIO
from flask import Flask, render_template, request, jsonify

MY_VERSION = 2.0
ICM_VERSION = 4.8
DEBUG = 0
lastAlarm = 0
secsAlarmMax = 60

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", ssl_context=None)


def checkICM():
    cmd = '~/ICM/.bin/nircmdc.exe'
    if OS == 'WINDOWS':
        cmd = r'..\ICM\.bin\nircmdc.exe'
    if not os.path.exists(cmd):
        print("Por favor ejecute los siguientes comandos:\n")
        print("  cd\n  git clone https://github.com/nelbren/ICM.git")
        exit(4)


def checkUpdate():
    url = 'https://raw.githubusercontent.com/nelbren'
    url += '/ICMd/refs/heads/main/app.py'
    response = requests.get(url)
    if response.status_code == 200:
        content = response.text
        match = re.search(r"MY_VERSION\s*=\s*(\d+\.\d+)", content)
        if match:
            version = match.group(1)
            version = float(version)
            if version != MY_VERSION:
                print(f"💻 ICMd v{MY_VERSION} != 🌐 ICMd v{version}"
                      " -> Please update, with: git pull")
                exit(1)
        else:
            print("No se encontró la versión.")
            exit(2)
    else:
        print(f"Error al acceder a la página: {response.status_code}")
        exit(3)


def sizeof_fmt(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


def get_status_row_color(row, last_update, status, ignored):
    elapsed = time.time() - last_update
    # print(elapsed)
    # print("STATUS ->", status)
    if status == "🌐":
        if not ignored:
            playSoundWithInternet(row)
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
    if OS in ["MACOS", "DARWIN"]:
        return "🍎"
    elif OS == "LINUX":
        return "🐧"
    elif OS == "WINDOWS":
        return "🪟"
    elif OS == "RASPBERRY":
        return "🍓"
    print("OS ->", OS)
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
        ignored = clients_status[id]["ignored"]
        OS = data.get("OS", "N/A")
        OS = get_os_emoji(OS)
        icmVersion = data.get("icmVersion", "N/A")
        icmTGZ = update_upload(id, name)
        # print('icmTGZ ->', icmTGZ)
        status = data.get("status", "N/A")
        # print(id, status, flush=True)
        status = get_status_emoji(status)
        # print(id, status, flush=True)
        # print(data, flush=True)
        ip = request.remote_addr
        elapsed = time.time() - timestamp
        color, status = get_status_row_color(row, time.time(), status, ignored)
        client_status = {
            "row": row,
            "name": name,
            "last_update": time.time(),
            "icmVersion": icmVersion,
            "icmTGZ": icmTGZ,
            "OS": OS,
            "status": status,
            "ip": ip,
            "color": color,
            # "ignored": False
            "ignored": ignored
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
                    "icmTGZ": icmTGZ,
                    "OS": OS
                }
        # print(f"{id} -> {data}", flush=True)
        # print('update->', data)
        socketio.emit('update_status', data)
        return jsonify({"message": "Updated successfully"}), 200
    else:
        print(f"❌🆔{id}❓UNKNOWN")
    return jsonify({"error": "Invalid data"}), 400


def get_details(uploadDst):
    stat = os.stat(uploadDst)
    f1 = time.ctime(stat.st_mtime)
    f2 = datetime.strptime(f1, "%a %b %d %H:%M:%S %Y") \
                 .strftime("%Y-%m-%d %H:%M:%S")
    sizeStr = sizeof_fmt(stat.st_size)
    return f2, sizeStr


def update_upload(id, name):
    currentDate = date.today()
    uploadDir = f'ICM/{currentDate}'
    name = name.replace(' ', '_')
    filename = f'{id}_{name}_ICM.tgz'
    uploadDst = f'{uploadDir}/{filename}'
    if os.path.exists(uploadDst):
        f2, sizeStr = get_details(uploadDst)
        # print('🆔', id, '🗃️', sizeStr)
        return f'{sizeStr}📦'
    return "N/A"


def update_uploads():
    currentDate = date.today()
    uploadDir = f'ICM/{currentDate}'
    if os.path.exists(uploadDir):
        print('📦 Uploads:')
        for filename in os.listdir(uploadDir):
            id = filename.split('_')[0]
            uploadDst = f'{uploadDir}/{filename}'
            f2, sizeStr = get_details(uploadDst)
            client_status = clients_status[id]
            client_status['icmTGZ'] = f'{sizeStr}📦'
            clients_status[id] = client_status
            print('🆔', id, '🗃️', client_status['icmTGZ'])
        print()


def playSound(phrase):
    global lastAlarm
    nowAlarm = time.time()
    secsAlarm = nowAlarm - lastAlarm
    if secsAlarm <= secsAlarmMax:
        if DEBUG:
            print('Ignorar alarma! ', secsAlarm, '<=', secsAlarmMax)
        return
    lastAlarm = nowAlarm
    if OS == "WINDOWS":
        cmd = r'..\ICM\.bin\nircmdc.exe'
        os.system(cmd + f' speak text "{phrase}"')
    else:
        listCmd = ['say', f'{phrase}']
        subprocess.run(listCmd)


def playSoundAtEnd(number):
    global lastAlarm
    lastAlarm = 0
    if OS == "WINDOWS":
        phrase = 'Great. I have some good news. '
        phrase += f'The good news is that player number {number} has finished.'
    else:
        phrase = 'Fenomenal. Tengo una noticia buena. '
        phrase += f'La buena es que el jugador numero {number} ha finalizado. '
    playSound(phrase)


def playSoundWithInternet(number):
    if OS == "WINDOWS":
        phrase = 'Terrible. I have bad news and good news. '
        phrase += "The good news is that I've identified "
        phrase += f'player number {number}.'
        phrase += 'The bad news is that he has an internet connection.'
    else:
        phrase = 'Terrible. Tengo una noticia mala y una buena. '
        phrase += 'La buena es que he identificado'
        phrase += f'al jugador numero {number}. '
        phrase += 'La mala es que cuenta con una conexión a internet.'
    playSound(phrase)


@app.route('/upload/<id>', methods=['GET', 'POST'])
def upload(id):
    if request.method == 'POST':
        if id in clients_status:
            currentDate = date.today()
            name = clients_status[id]["name"]
            name = name.replace(' ', '_')
            uploadDir = f'ICM/{currentDate}'
            if not os.path.exists(uploadDir):
                os.makedirs(uploadDir)
            uploadName = f'{id}_{name}_ICM.tgz'
            uploadDst = f'{uploadDir}/{uploadName}'
            file = request.files['filedata']
            # print(timestamp, file)
            file.save(uploadDst)
            f2, sizeStr = get_details(uploadDst)
            detail = f2 + ' | ' + sizeStr
            client_status = clients_status[id]
            client_status['icmTGZ'] = f'{sizeStr}📦'
            client_status['id'] = id
            client_status['ignored'] = True
            clients_status[id] = client_status
            print('upload->', client_status)
            socketio.emit('update_status', client_status)
            number = client_status['row']
            playSoundAtEnd(number)
            return f'¡📦 {uploadName} ({detail}) ✅ Upload successful 😎!'
        else:
            return f'🚫 Nice try {id} 🙃!'


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
        ignored = info.get("ignored", False)
        color, status = get_status_row_color(
            info['row'], info["last_update"], status, ignored)
        ip = info.get("ip", "N/A")
        OS = info.get("OS", "N/A")
        icmVersion = info.get("icmVersion", "N/A")
        icmTGZ = info.get("icmTGZ", "N/A")
        if DEBUG:
            print(f"🔃➜🌐➜💻{ip}🆔{id}")
        # print("request_status ->", ip)
        # print(id, info)
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
                    "icmVersion": icmVersion,
                    "icmTGZ": icmTGZ
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


OS = getOSM()
checkICM()
checkUpdate()
osEmoji = get_os_emoji(OS)
currentDate = date.today()
clients_status = getStudents()
print(f'\n⚡️ Energizado por 🌐 ICMd v{MY_VERSION}'
      f' 🔌 ejecutandose en {osEmoji} el {currentDate}\n')
update_uploads()

if __name__ == '__main__':
    socketio.run(app, debug=True)
