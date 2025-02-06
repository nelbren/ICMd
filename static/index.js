var audioEnabled = false;
var audioButton = document.getElementById("audio-toggle");
let lastResponseTime = Date.now();

function enableAudio() {
    if (!audioEnabled) {
        document.getElementById("alert-sound").play().catch(() => {})
        audioEnabled = true;
        updateAudioButton();
    }
}

function updateAudioButton() {
    if (audioEnabled) {
        audioButton.textContent = "🔊";
        audioButton.classList.remove("audio-off");
        audioButton.classList.add("audio-on");
    } else {
        audioButton.textContent = "🔇";
        audioButton.classList.remove("audio-on");
        audioButton.classList.add("audio-off");
    }
}

var socket = io();
var alertSound = document.getElementById("alert-sound");

socket.on('update_status', function(data) {
    let table = document.getElementById("clients-table");
    let row = document.getElementById("client-" + data.id);
    let now = new Date();

    let formattedTime = "N/A";
    let elapsedText = "N/A";
    let elapsedSeconds = 0;

    if (data.timestamp) {
        let timestamp = new Date(data.timestamp * 1000);
        formattedTime = timestamp.toLocaleTimeString('es-ES', { hour12: false }).padStart(8, '0');
        elapsedSeconds = Math.floor((now - timestamp) / 1000);
        elapsedText = elapsedSeconds + "s";
    }

    if (!row) {
        row = table.insertRow();
        row.id = "client-" + data.id;
        row.insertCell(0).textContent = table.rows.length;  // Número de fila
        row.insertCell(1).textContent = data.id;  // ID del usuario
        row.insertCell(2).textContent = data.name || "Desconocido";  // Nombre
        row.insertCell(3).textContent = data.ip || "N/A";  // IP
        row.insertCell(4).textContent = formattedTime;  // Última actualización
        row.insertCell(5).textContent = elapsedText;  // Tiempo transcurrido
        row.insertCell(6).textContent = data.status || "❌";  // Estado

        // Celda de Ignorar con checkbox
        let ignoreCell = row.insertCell(7);
        let checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.checked = getIgnoreStatus(data.id);
        checkbox.onchange = function() {
            updateBackgroundColor();
        };
        checkbox.className = "ignore-checkbox";
        checkbox.setAttribute('data-user-id' , data.id);


        ignoreCell.appendChild(checkbox);
    } else {
        row.cells[1].textContent = data.id;
        row.cells[2].textContent = data.name || "Desconocido";
        row.cells[3].textContent = data.ip || "N/A";
        row.cells[4].textContent = formattedTime;
        row.cells[5].textContent = elapsedText;
        row.cells[6].textContent = data.status || "❌";
    }

    let isIgnored = getIgnoreStatus(data.id);
    row.className = isIgnored ? "gray-row" : data.color;

    // Aplicar color al campo de Estado
    let statusCell = row.cells[6];
    if (!isIgnored) {
        if (data.status === "✔️") {
            statusCell.className = "status-green";
        } else {
            if (data.status === "🌐") 
                statusCell.className = "status-red";
            else
                statusCell.className = "status-yellow";
            if (!isIgnored && audioEnabled) {
                alertSound.play().catch(err => console.warn("Error al reproducir sonido:", err));
            }
        }
    }

    updateBackgroundColor();
});

function updateBackgroundColor() {
    let statusCells = document.querySelectorAll("#clients-table td:nth-child(7)"); 
    let hasRed = false, hasYellow = false;

    statusCells.forEach(cell => {
        let row = cell.parentNode;
        let isIgnored = row.querySelector("input[type='checkbox']").checked;
        let statusCell = row.cells[6];

        if (isIgnored) {
            row.className = "gray-row"
            statusCell.className  = "gray-row"
        } else {
            if (cell.className === "status-red") {
                hasRed = true;
            } else if (cell.className === "status-yellow") { 
                hasYellow = true;
            }
        }
    });

    if (hasRed) {
        document.body.style.backgroundColor = "pink";
    } else if (hasYellow) {
        document.body.style.backgroundColor = "Khaki";
    } else {
        document.body.style.backgroundColor = "PaleGreen"; // "green";
    }
}

function getIgnoreStatus(userId) {
    let ignoredUsers = JSON.parse(localStorage.getItem("ignoredUsers")) || {};
    return ignoredUsers[userId];
}

socket.on('update_counters', function(data) {
    document.getElementById("ok-count").innerText = `${data.ok} ✔`;
    document.getElementById("warning-count").innerText = `${data.warning} ⚠️`;
    document.getElementById("critical-count").innerText = `${data.critical} ❌`;
    document.getElementById("ignore-count").innerText = `${data.ignore} ❎`;
    document.getElementById("active-count").innerText = `${data.active} ✅`;
});

document.addEventListener("change", function (event) {
    if (event.target.classList.contains("ignore-checkbox")) {
        let userId = event.target.dataset.userId;
        let isIgnored = event.target.checked;

        // Guardar en localStorage
        let ignoredUsers = JSON.parse(localStorage.getItem("ignoredUsers")) || {};
        ignoredUsers[userId] = isIgnored;
        localStorage.setItem("ignoredUsers", JSON.stringify(ignoredUsers));

        // Enviar la actualización al backend
        socket.emit("update_ignore_status", { id: userId, ignored: isIgnored });
    }
});

document.addEventListener("DOMContentLoaded", function () {
    actualizarCheckboxes();
});

function actualizarCheckboxes() {
    // console.log("actualizarCheckboxes");
    let ignoredUsers = JSON.parse(localStorage.getItem("ignoredUsers")) || {};

    for (let userId in ignoredUsers) {
        let checkbox = document.querySelector(`.ignore-checkbox[data-user-id='${userId}']`);
        
        if (checkbox) {
            isIgnored = ignoredUsers[userId];
            // console.log("fijando ->", userId, isIgnored);
            checkbox.checked = ignoredUsers[userId];
            // Enviar la actualización al backend
            // console.log("update_ignore_status", { id: userId, ignored: isIgnored });
            socket.emit("update_ignore_status", { id: userId, ignored: isIgnored });
        /*
        } else {
            console.warn(`Checkbox para el usuario ${userId} no encontrado.`);
        */
        }
    }
}

// Función para actualizar el indicador
function updateStatus() {
    const now = Date.now();
    const elapsed = now - lastResponseTime;
    const statusElement = document.getElementById("server-status");

    if (elapsed < 5000) {
        statusElement.innerHTML = "🙂";
        statusElement.style.backgroundColor = "green";
    } else {
        statusElement.innerHTML = "☹️";
        statusElement.style.backgroundColor = "red";
    }
}

// Escuchar respuesta del backend
socket.on('pong_client', (data) => { lastResponseTime = Date.now(); updateStatus(); });
socket.emit('request_status');

// Actualizar la tabla cada 5 segundos
setInterval(() => { socket.emit('request_status'); }, 5000);
setTimeout(actualizarCheckboxes, 500);
setInterval(() => { socket.emit('ping_server'); updateStatus(); }, 400);
