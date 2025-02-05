# Internet Connection Monitor daemon- nelbren@nelbren.com @ 2025-01-31 - v1.0
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import time
from canvas import getStudents
import socket


DEBUG = 0

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", ssl_context=None)

# Diccionario para almacenar el estado de los clientes
clients_status = getStudents()  # {}


def get_status_row_color(last_update, status):
    elapsed = time.time() - last_update
    # print(elapsed)
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


@app.route('/')
def index():
    server_ip = get_server_ip()
    # print(f"Server IP: {server_ip}")
    return render_template('index.html', server_ip=server_ip)


@app.route('/update', methods=['POST'])
def update():
    timestamp = time.time()
    data = request.json
    id = data.get("id")
    if id:
        row = clients_status[id]["row"]
        name = clients_status[id]["name"]
        status = data.get("status", "N/A")
        ip = request.remote_addr
        elapsed = time.time() - timestamp
        color, status = get_status_row_color(time.time(), status)
        client_status = {
            "row": row,
            "name": name,
            "last_update": time.time(),
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
                    "ip": ip
                }
        socketio.emit('update_status', data)
        return jsonify({"message": "Updated successfully"}), 200
    return jsonify({"error": "Invalid data"}), 400


@socketio.on('request_status')
def send_status():
    """Envía el estado actualizado de los clientes con un índice de fila."""
    ok_count = 0
    warning_count = 0
    critical_count = 0
    ignore_count = 0
    active_count = 0
    # active_count = 0
    # inactive_count = 0
    # print(clients_status)
    for index, (id, info) in enumerate(clients_status.items(), start=1):
        # print("send_status - info ->", info)
        elapsed = time.time() - info["last_update"]
        status = info.get("status", "N/A")
        color, status = get_status_row_color(
            info["last_update"], status)
        ip = info.get("ip", "N/A")
        if DEBUG:
            print(f"🔃➜🌐➜💻{ip}🆔{id}")
        # print("request_status ->", ip)
        # print(id, info)
        ignored = info.get("ignored", False)
        if ignored:
            ignore_count += 1
        else:
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
        # "active": active_count,
        # "inactive": inactive_count
    })


@socketio.on('update_ignore_status')
def update_ignore_status(data):
    user_id = data.get("id")
    ignored = data.get("ignored")

    if user_id in clients_status:
        clients_status[user_id]["ignored"] = ignored

    # print('update_ignore_status', user_id, ignored)


def get_server_ip():
    hostname = socket.gethostname()
    ip_list = socket.getaddrinfo(hostname, None, proto=socket.IPPROTO_TCP)
    for ip in ip_list:
        if ip[4][0] and not ip[4][0].startswith("127."):
            return ip[4][0]  # Retorna la primera IP no local encontrada
    return "127.0.0.1"  # Si no encuentra otra, retorna localhost

if __name__ == '__main__':
    socketio.run(app, debug=True)
