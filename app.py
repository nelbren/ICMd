# Internet Connection Monitor daemon- nelbren@nelbren.com @ 2025-01-31 - v1.0
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import time
from canvas import getStudents

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", ssl_context=None)

# Diccionario para almacenar el estado de los clientes
clients_status = getStudents()  # {}


def get_status_color(last_update):
    elapsed = time.time() - last_update
    # print(elapsed)
    if elapsed < 25:
        return "green"
    elif elapsed < 40:
        return "yellow"
    elif elapsed < 55:
        return "red"
    else:
        return "red"


@app.route('/')
def index():
    return render_template('index.html')


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
        client_status = {
            "row": row,
            "name": name,
            "last_update": time.time(),
            "status": status,
            "ip": ip,
        }
        print("🔃→", id, client_status)
        clients_status[id] = client_status
        elapsed = time.time() - timestamp
        color = get_status_color(time.time())
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
    for index, (id, info) in enumerate(clients_status.items(), start=1):
        # print("send_status - info ->", info)
        elapsed = time.time() - info["last_update"]
        color = get_status_color(info["last_update"])
        data = {
                    "row": index,
                    "id": id,
                    "name": info["name"],
                    "timestamp": info["last_update"],
                    "elapsed": elapsed,
                    "color": color,
                    "status": info["status"],
                    "ip": info["ip"]
                }
        socketio.emit('update_status', data)


if __name__ == '__main__':
    socketio.run(app, debug=True)
