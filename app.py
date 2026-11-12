import streamlit as st
import json
import os

st.set_page_config(
    page_title="JARVIS HUD",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="collapsed"
)

hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
        padding-left: 0rem !important;
        padding-right: 0rem !important;
        max-width: 100% !important;
    }
    .stApp { 
        background-color: #000000; 
        overflow: hidden !important; 
        margin: 0 !important;
        padding: 0 !important;
    }
    iframe {
        display: block;
        border: none;
        margin: 0 auto;
    }
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

AGENDA_FILE = "agenda.json"

if not os.path.exists(AGENDA_FILE):
    with open(AGENDA_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)

hud_html = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <style>
        * { box-sizing: border-box; }
        html, body {
            background-color: #010a17;
            margin: 0; padding: 0;
            width: 100vw; height: 100vh;
            overflow: hidden;
            display: flex; justify-content: center; align-items: center;
            font-family: 'Consolas', monospace;
            transition: background-color 1s ease;
        }
        .hud-container {
            position: relative;
            width: 100vw; height: 100vh;
            display: flex; justify-content: center; align-items: center;
        }
        canvas {
            position: absolute; top: 0; left: 0;
            transition: opacity 1s ease;
        }
        .core-text {
            position: absolute; text-align: center; color: #00f3ff;
            z-index: 10; pointer-events: none;
            transition: opacity 1s ease;
        }
        .core-text h1 {
            margin: 0; font-size: 38px; letter-spacing: 8px;
            color: #ffffff; text-shadow: 0 0 20px #00f3ff, 0 0 40px #00f3ff;
            font-weight: 800; transition: color 1s ease, text-shadow 1s ease;
        }
        .core-text p {
            margin: 8px 0 0 0; font-size: 11px; color: #38bdf8;
            letter-spacing: 4px; text-transform: uppercase; transition: color 1s ease;
        }
        .status-bar {
            position: absolute; bottom: 25px; color: #0ea5e9;
            font-size: 11px; letter-spacing: 3px; text-transform: uppercase;
            background: rgba(1, 10, 23, 0.85); padding: 8px 20px;
            border: 1px solid #00f3ff44; border-radius: 4px;
            box-shadow: 0 0 12px rgba(0, 243, 255, 0.25);
            cursor: pointer; transition: opacity 1s ease, border-color 1s ease, color 1s ease;
            z-index: 20;
            user-select: none;
        }
        .diagnostic-panel {
            position: absolute; top: 20px; right: 25px;
            background: rgba(1, 10, 23, 0.85); border: 1px solid #00f3ff55;
            border-radius: 6px; padding: 10px 16px; color: #00f3ff;
            font-size: 11px; letter-spacing: 2px;
            box-shadow: 0 0 15px rgba(0, 243, 255, 0.2);
            z-index: 20; pointer-events: none; text-align: right;
            transition: opacity 1s ease;
        }
        .diagnostic-panel .clock {
            font-size: 18px; font-weight: bold; color: #ffffff;
            text-shadow: 0 0 8px #00f3ff; margin-bottom: 2px;
        }
        .diagnostic-panel .sys-info { font-size: 10px; color: #38bdf8; }

        #windowsLayer {
            position: absolute; top: 0; left: 0;
            width: 100vw; height: 100vh;
            pointer-events: none;
            z-index: 25;
        }
        .hud-window {
            position: absolute;
            background: rgba(1, 15, 35, 0.9);
            border: 1.5px solid #00f3ff;
            border-radius: 6px;
            padding: 15px 20px 15px 25px;
            color: #00f3ff;
            font-size: 12px;
            letter-spacing: 1.5px;
            box-shadow: 0 0 20px rgba(0, 243, 255, 0.3), inset 0 0 10px rgba(0, 243, 255, 0.15);
            pointer-events: auto;
            backdrop-filter: blur(4px);
            animation: fadeInWindow 0.4s ease forwards;
            min-width: 280px;
            max-width: 350px;
        }
        @keyframes fadeInWindow {
            from { opacity: 0; transform: scale(0.9); }
            to { opacity: 1; transform: scale(1); }
        }
        .hud-window .close-btn {
            position: absolute;
            top: 6px;
            left: 8px;
            color: #ff2a2a;
            border: 1px solid #ff2a2a55;
            background: rgba(50, 0, 0, 0.5);
            width: 18px; height: 18px;
            font-size: 11px;
            font-weight: bold;
            display: flex; justify-content: center; align-items: center;
            border-radius: 3px;
            cursor: pointer;
            box-shadow: 0 0 5px rgba(255, 42, 42, 0.4);
            transition: background 0.2s;
        }
        .hud-window .close-btn:hover {
            background: rgba(255, 42, 42, 0.8);
            color: #ffffff;
        }
        .hud-window h3 {
            margin: 0 0 8px 0;
            font-size: 13px;
            color: #ffffff;
            border-bottom: 1px dashed #00f3ff55;
            padding-bottom: 4px;
            text-transform: uppercase;
            letter-spacing: 2px;
            text-align: right;
        }
        .hud-window ul {
            margin: 0; padding-left: 15px; color: #38bdf8;
        }
        .hud-window li {
            margin-bottom: 4px;
        }
    </style>
</head>
<body>
    <div class="hud-container">
        <canvas id="hudCanvas"></canvas>
        <div class="core-text" id="coreTextBox">
            <h1 id="jarvisTitle">J.A.R.V.I.S</h1>
            <p id="jarvisStatus">SISTEMA EN LÍNEA</p>
        </div>
        <div class="diagnostic-panel" id="diagPanel">
            <div class="clock" id="hudClock">00:00:00</div>
            <div class="sys-info">CPU: 4.2% | MEM: 1.4GB</div>
            <div class="sys-info" id="modeInfo">MODO: ESTÁNDAR</div>
        </div>
        <div class="status-bar" id="audioStatus" onclick="toggleEscuchaManual()">⚡ HAZ CLIC PARA ACTIVAR CONTROL DE VOZ</div>
        <div id="windowsLayer"></div>
    </div>

    <script>
        const canvas = document.getElementById('hudCanvas');
        const ctx = canvas.getContext('2d');
        
        function resize() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }
        window.addEventListener('resize', resize);
        resize();

        let recordatorios = [];
        let estadoPendienteAMPM = null;
        let recognition = null;
        let controlVozActivo = false;
        let modoCineActivo = false;
        let activeWindows = [];

        // BASE DE DATOS ACADÉMICA PERSISTENTE EN LOCALSTORAGE
        let baseDatosAcademica = JSON.parse(localStorage.getItem('jarvis_db_academica') || JSON.stringify({
            "lunes": {
                titulo: "HORARIO: LUNES",
                items: [
                    "Matemáticas: 1:00 PM a 2:00 PM",
                    "Francés: 2:05 PM a 3:30 PM",
                    "FSN: 3:35 PM a 4:00 PM",
                    "GHC: 4:05 PM a 5:30 PM"
                ]
            },
            "frances": {
                titulo: "MATERIA: FRANCÉS",
                items: [
                    "Notas: 16 - 20 (Promedio: 18)",
                    "Profesor: María Pérez",
                    "Dificultad: Exigente con ilustraciones y formato de cuaderno"
                ]
            }
        }));

        function guardarDB() {
            localStorage.setItem('jarvis_db_academica', JSON.stringify(baseDatosAcademica));
        }

        function crearVentanaFlotante(contenidoHTML, tituloVentana = "REGISTRO HUD") {
            const layer = document.getElementById('windowsLayer');
            
            if (activeWindows.length >= 5) {
                const oldestId = activeWindows.shift();
                const oldEl = document.getElementById(oldestId);
                if (oldEl) oldEl.remove();
            }

            const winId = 'hud_win_' + Date.now() + '_' + Math.floor(Math.random()*1000);
            activeWindows.push(winId);

            const posX = Math.floor(Math.random() * (window.innerWidth - 400 - 100)) + 50;
            const posY = Math.floor(Math.random() * (window.innerHeight - 300 - 100)) + 80;

            const winDiv = document.createElement('div');
            winDiv.className = 'hud-window';
            winDiv.id = winId;
            winDiv.style.left = posX + 'px';
            winDiv.style.top = posY + 'px';

            winDiv.innerHTML = `
                <div class="close-btn" onclick="cerrarVentana('${winId}')" title="Cerrar ventana">X</div>
                <h3>${tituloVentana}</h3>
                <div>${contenidoHTML}</div>
            `;

            layer.appendChild(winDiv);
        }

        function cerrarVentana(winId) {
            const el = document.getElementById(winId);
            if (el) {
                el.remove();
                activeWindows = activeWindows.filter(id => id !== winId);
            }
        }

        function mostrarPaginaCincoVacia(queryText) {
            let html = `<ul><li>Sin información registrada sobre "${queryText}".</li><li>Sin informacion actual.</li></ul>`;
            crearVentanaFlotante(html, "AVISO: SIN DATOS (PÁG 5)");
        }

        setInterval(() => {
            const now = new Date();
            const horaActualStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false });
            document.getElementById('hudClock').innerText = now.toLocaleTimeString();

            for (let i = recordatorios.length - 1; i >= 0; i--) {
                if (recordatorios[i].hora === horaActualStr) {
                    let rec = recordatorios.splice(i, 1)[0];
                    if (modoSueno || modoCineActivo) cambiarTema('normal');
                    hablar("Ey, Señor, le recuerdo que tiene pendiente " + rec.mensaje + ". Sugiero atenderlo a la brevedad.");
                    document.getElementById('jarvisStatus').innerText = "RECORDATORIO ACTIVO";
                }
            }
        }, 1000);

        let angleMain = 0, angleInner = 0, angleOuter = 0;
        let modoSueno = false, modoSilencio = false, pulseTime = 0;

        let theme = {
            primary: '#00f3ff',
            secondary: '#38bdf8',
            darkLine: '#0284c7',
            dimLine: 'rgba(2, 40, 80, 0.35)',
            glow: 'rgba(0, 243, 255, 0.9)'
        };

        function emitirPitido() {
            if (modoSilencio) return;
            try {
                const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                const osc = audioCtx.createOscillator();
                const gain = audioCtx.createGain();
                osc.type = 'sine';
                osc.frequency.setValueAtTime(1200, audioCtx.currentTime);
                gain.gain.setValueAtTime(0.08, audioCtx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + 0.12);
                osc.connect(gain);
                gain.connect(audioCtx.destination);
                osc.start();
                osc.stop(audioCtx.currentTime + 0.12);
            } catch(e) {}
        }

        function cambiarTema(modo) {
            modoSueno = false;
            modoCineActivo = false;
            canvas.style.opacity = "1";
            document.body.style.backgroundColor = "#010a17";
            document.getElementById('audioStatus').style.opacity = "1";
            document.getElementById('diagPanel').style.opacity = "1";
            document.getElementById('coreTextBox').style.opacity = "1";

            if (modo === 'sigilo') {
                theme.primary = '#ff2a2a'; theme.secondary = '#f87171';
                theme.darkLine = '#991b1b'; theme.dimLine = 'rgba(80, 10, 10, 0.35)';
                document.getElementById('jarvisTitle').style.textShadow = "0 0 20px #ff2a2a, 0 0 40px #ff2a2a";
                document.getElementById('jarvisStatus').style.color = "#f87171";
                document.getElementById('modeInfo').innerText = "MODO: SIGILO";
            } else {
                theme.primary = '#00f3ff'; theme.secondary = '#38bdf8';
                theme.darkLine = '#0284c7'; theme.dimLine = 'rgba(2, 40, 80, 0.35)';
                document.getElementById('jarvisTitle').style.textShadow = "0 0 20px #00f3ff, 0 0 40px #00f3ff";
                document.getElementById('jarvisStatus').style.color = "#38bdf8";
                document.getElementById('modeInfo').innerText = "MODO: ESTÁNDAR";
            }
        }

        function activarModoSueno() {
            modoSueno = true;
            document.body.style.backgroundColor = "#000000";
            canvas.style.opacity = "0.2";
            document.getElementById('audioStatus').style.opacity = "0.4";
            document.getElementById('diagPanel').style.opacity = "0.3";
            theme.primary = '#0284c7'; theme.secondary = '#0369a1';
            theme.darkLine = '#0c4a6e'; theme.dimLine = 'rgba(2, 20, 40, 0.15)';
            document.getElementById('jarvisTitle').style.textShadow = "0 0 10px #0284c7";
            document.getElementById('jarvisStatus').style.color = "#0284c7";
            document.getElementById('jarvisStatus').innerText = "REPOSO PROFUNDO";
            document.getElementById('modeInfo').innerText = "MODO: SUEÑO";
        }

        function activarModoCine() {
            modoCineActivo = true;
            document.body.style.backgroundColor = "#000000";
            canvas.style.opacity = "0";
            document.getElementById('coreTextBox').style.opacity = "0";
            document.getElementById('diagPanel').style.opacity = "0.15";
            document.getElementById('audioStatus').style.opacity = "0.3";
            document.getElementById('modeInfo').innerText = "MODO: CINE";
        }

        let timerInterval = null, tiempoRestanteSegundos = 0;

        function drawBackgroundGrid() {
            ctx.save(); ctx.strokeStyle = theme.dimLine; ctx.lineWidth = 1;
            for(let x = 0; x < canvas.width; x += 40) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, canvas.height); ctx.stroke(); }
            for(let y = 0; y < canvas.height; y += 40) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(canvas.width, y); ctx.stroke(); }
            ctx.restore();
        }

        function drawNodeDot(x, y, radius = 4) {
            ctx.beginPath(); ctx.arc(x, y, radius, 0, Math.PI * 2);
            ctx.fillStyle = theme.primary; ctx.shadowBlur = modoSueno ? 3 : 10; ctx.shadowColor = theme.primary; ctx.fill();
        }

        function drawTargetNode(x, y, size = 26) {
            ctx.save(); ctx.strokeStyle = theme.primary; ctx.lineWidth = 1.8; ctx.shadowBlur = modoSueno ? 3 : 10; ctx.shadowColor = theme.primary;
            ctx.beginPath(); ctx.arc(x, y, size, 0, Math.PI * 2); ctx.stroke();
            ctx.beginPath(); ctx.arc(x, y, size * 0.65, 0, Math.PI * 2); ctx.strokeStyle = theme.secondary; ctx.stroke();
            ctx.beginPath(); ctx.arc(x, y, size * 0.3, 0, Math.PI * 2); ctx.stroke();
            ctx.beginPath(); ctx.arc(x, y, 3, 0, Math.PI * 2); ctx.fillStyle = theme.primary; ctx.fill();
            ctx.restore();
        }

        function drawPCB(cx, cy) {
            ctx.save(); ctx.strokeStyle = theme.darkLine; ctx.lineWidth = 2; ctx.shadowBlur = modoSueno ? 2 : 8; ctx.shadowColor = theme.primary;
            let lY1 = cy - 190; ctx.beginPath(); ctx.moveTo(0, lY1); ctx.lineTo(cx - 380, lY1); ctx.lineTo(cx - 320, lY1 + 60); ctx.lineTo(cx - 230, lY1 + 60); ctx.stroke(); drawNodeDot(cx - 380, lY1); drawNodeDot(cx - 230, lY1 + 60);
            let lY2 = cy - 90; ctx.beginPath(); ctx.moveTo(0, lY2); ctx.lineTo(cx - 340, lY2); ctx.lineTo(cx - 280, lY2 + 30); ctx.lineTo(cx - 220, lY2 + 30); ctx.stroke(); drawNodeDot(cx - 340, lY2); drawNodeDot(cx - 220, lY2 + 30);
            let lY3 = cy + 120; ctx.beginPath(); ctx.moveTo(0, lY3); ctx.lineTo(cx - 400, lY3); ctx.lineTo(cx - 330, lY3 - 50); ctx.lineTo(cx - 230, lY3 - 50); ctx.stroke(); drawNodeDot(cx - 400, lY3); drawNodeDot(cx - 230, lY3 - 50);
            let lY4 = cy + 210; ctx.beginPath(); ctx.moveTo(0, lY4); ctx.lineTo(cx - 300, lY4); ctx.lineTo(cx - 250, lY4 - 40); ctx.lineTo(cx - 210, lY4 - 40); ctx.stroke();
            ctx.strokeStyle = theme.secondary; ctx.strokeRect(50, cy - 230, 120, 48); ctx.strokeRect(65, cy - 220, 40, 28); drawTargetNode(80, cy + 190, 26);
            let rY1 = cy - 200; ctx.beginPath(); ctx.moveTo(canvas.width, rY1); ctx.lineTo(cx + 400, rY1); ctx.lineTo(cx + 330, rY1 + 60); ctx.lineTo(cx + 230, rY1 + 60); ctx.stroke(); drawNodeDot(cx + 400, rY1); drawNodeDot(cx + 230, rY1 + 60);
            let rY2 = cy - 60; ctx.beginPath(); ctx.moveTo(canvas.width, rY2); ctx.lineTo(cx + 350, rY2); ctx.lineTo(cx + 290, rY2 - 30); ctx.lineTo(cx + 230, rY2 - 30); ctx.stroke(); drawNodeDot(cx + 350, rY2);
            let rY3 = cy + 140; ctx.beginPath(); ctx.moveTo(canvas.width, rY3); ctx.lineTo(cx + 380, rY3); ctx.lineTo(cx + 310, rY3 - 60); ctx.lineTo(cx + 220, rY3 - 60); ctx.stroke(); drawNodeDot(cx + 380, rY3); drawNodeDot(cx + 220, rY3 - 60);
            drawTargetNode(canvas.width - 90, cy - 200, 26);
            ctx.strokeStyle = theme.primary; ctx.strokeRect(cx + 290, cy + 20, 75, 95);
            for(let i = 0; i < 4; i++) { ctx.fillStyle = theme.primary; ctx.fillRect(cx + 304 + (i * 13), cy + 35, 6, 65); }
            let grad = ctx.createLinearGradient(cx - 320, cy, cx + 320, cy); grad.addColorStop(0, 'transparent'); grad.addColorStop(0.5, theme.primary); grad.addColorStop(1, 'transparent');
            ctx.strokeStyle = grad; ctx.lineWidth = 1.5; ctx.beginPath(); ctx.moveTo(cx - 320, cy); ctx.lineTo(cx + 320, cy); ctx.stroke();
            ctx.restore();
        }

        function drawHUD() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            let cx = canvas.width / 2; let cy = canvas.height / 2;
            drawBackgroundGrid(); drawPCB(cx, cy);

            let speedMultiplier = modoSueno ? 0.2 : 1.0;
            angleMain += 0.004 * speedMultiplier; angleInner -= 0.006 * speedMultiplier; angleOuter += 0.002 * speedMultiplier;

            ctx.save(); ctx.translate(cx, cy); ctx.rotate(angleOuter); ctx.strokeStyle = theme.primary; ctx.lineWidth = 3; ctx.shadowBlur = modoSueno ? 5 : 15; ctx.shadowColor = theme.primary;
            ctx.beginPath(); ctx.arc(0, 0, 235, 0, Math.PI * 1.35); ctx.stroke(); ctx.beginPath(); ctx.arc(0, 0, 235, Math.PI * 1.45, Math.PI * 1.85); ctx.stroke(); ctx.restore();

            ctx.save(); ctx.translate(cx, cy); ctx.rotate(-angleOuter * 1.5); ctx.fillStyle = theme.secondary;
            for (let i = 0; i < 18; i++) { let angle = (i * 7.5) * Math.PI / 180 + Math.PI * 0.2; ctx.fillRect(Math.cos(angle) * 215, Math.sin(angle) * 215, 4, 4); }
            ctx.restore();

            ctx.save(); ctx.translate(cx, cy); ctx.rotate(angleInner); ctx.strokeStyle = theme.secondary; ctx.lineWidth = 1.5;
            for (let i = 0; i < 90; i++) { ctx.beginPath(); let angle = (i * 4) * Math.PI / 180; let len = (i % 5 === 0) ? 12 : 6; ctx.moveTo(Math.cos(angle) * 195, Math.sin(angle) * 195); ctx.lineTo(Math.cos(angle) * (195 - len), Math.sin(angle) * (195 - len)); ctx.stroke(); }
            ctx.restore();

            ctx.save(); ctx.translate(cx, cy); ctx.rotate(angleMain * 0.8); ctx.fillStyle = theme.primary;
            for (let i = 0; i < 24; i++) { let angle = (i * 3.5) * Math.PI / 180 + Math.PI * 0.75; ctx.fillRect(Math.cos(angle) * 172, Math.sin(angle) * 172, 5, 10); }
            ctx.restore();

            ctx.save(); ctx.translate(cx, cy); ctx.rotate(-angleMain * 0.5); ctx.fillStyle = theme.secondary; ctx.font = '11px Consolas, monospace';
            let zerosUpper = "0000000000"; for (let i = 0; i < zerosUpper.length; i++) { let angle = (i * 6) * Math.PI / 180 - Math.PI * 0.4; ctx.fillText(zerosUpper[i], Math.cos(angle) * 152, Math.sin(angle) * 152); }
            let zerosLower = "0000000000000"; for (let i = 0; i < zerosLower.length; i++) { let angle = (i * 6) * Math.PI / 180 + Math.PI * 0.6; ctx.fillText(zerosLower[i], Math.cos(angle) * 152, Math.sin(angle) * 152); }
            ctx.restore();

            pulseTime += 0.02;
            let pulseGlow = modoSueno ? (Math.sin(pulseTime) * 8 + 12) : 20;

            ctx.save(); ctx.beginPath(); ctx.arc(cx, cy, 118, 0, Math.PI * 2); ctx.fillStyle = modoSueno ? 'rgba(0, 0, 0, 0.98)' : 'rgba(1, 10, 23, 0.95)'; ctx.fill();
            ctx.strokeStyle = theme.primary; ctx.lineWidth = 3.5; ctx.shadowBlur = pulseGlow; ctx.shadowColor = theme.primary; ctx.stroke(); ctx.restore();

            requestAnimationFrame(drawHUD);
        }

        drawHUD();

        function hablar(texto) {
            if (modoSilencio) return;
            window.speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance(texto);
            utterance.lang = 'es-ES';
            utterance.rate = 1.0;
            window.speechSynthesis.speak(utterance);
        }

        function analizarHoraTexto(texto) {
            let match = texto.match(/(\d{1,2})[:\s]*(\d{2})?/);
            if (!match) return null;
            let hora = parseInt(match[1]);
            let min = match[2] ? parseInt(match[2]) : 0;
            let tienePeriodo = false;
            let esPM = false;

            if (texto.includes("p.m.") || texto.includes("pm") || texto.includes("tarde") || texto.includes("noche")) {
                tienePeriodo = true; esPM = true;
            } else if (texto.includes("a.m.") || texto.includes("am") || texto.includes("mañana")) {
                tienePeriodo = true; esPM = false;
            }

            return { hora: hora, min: min, tienePeriodo: tienePeriodo, esPM: esPM };
        }

        function formatearHoraHHMM(h, m) {
            let hStr = h < 10 ? "0" + h : "" + h;
            let mStr = m < 10 ? "0" + m : "" + m;
            return hStr + ":" + mStr;
        }

        function iniciarTemporizadorEnfoque(minutos) {
            cambiarTema('normal');
            if (timerInterval) { clearInterval(timerInterval); timerInterval = null; }
            tiempoRestanteSegundos = minutos * 60;
            hablar("Protocolo de enfoque activado por " + minutos + " minutos. He establecido el contador en marcha, Señor.");

            timerInterval = setInterval(() => {
                if (tiempoRestanteSegundos <= 0) {
                    clearInterval(timerInterval); timerInterval = null;
                    document.getElementById('jarvisStatus').innerText = "TIEMPO FINALIZADO";
                    hablar("El tiempo de enfoque programado ha concluido con éxito, Señor.");
                } else {
                    tiempoRestanteSegundos--;
                    let m = Math.floor(tiempoRestanteSegundos / 60), s = tiempoRestanteSegundos % 60;
                    document.getElementById('jarvisStatus').innerText = "ENFOQUE: " + (m < 10 ? "0"+m : m) + ":" + (s < 10 ? "0"+s : s);
                }
            }, 1000);
        }

        function detenerTemporizadorEnfoque() {
            if (timerInterval) {
                clearInterval(timerInterval); timerInterval = null;
                document.getElementById('jarvisStatus').innerText = "SISTEMA ACTIVO";
                hablar("Sesión de enfoque cancelada a petición suya, Señor. Los sistemas han regresado a la normalidad.");
            } else { hablar("Actualmente no hay ninguna sesión de enfoque activa en curso, Señor."); }
        }

        function obtenerTareas() { return JSON.parse(localStorage.getItem('jarvis_tareas') || '[]'); }
        function guardarTarea(tarea) { let t = obtenerTareas(); t.push(tarea); localStorage.setItem('jarvis_tareas', JSON.stringify(t)); }
        function eliminarTareaUnica(criterio) {
            let t = obtenerTareas();
            if (t.length === 0) return "No hay tareas registradas en la agenda, Señor.";
            let num = parseInt(criterio);
            if (!isNaN(num) && num > 0 && num <= t.length) {
                let borrada = t.splice(num - 1, 1)[0];
                localStorage.setItem('jarvis_tareas', JSON.stringify(t));
                return "La tarea número " + num + " ha sido eliminada de su registro correctamente.";
            }
            let idx = t.findIndex(item => item.toLowerCase().includes(criterio.toLowerCase()));
            if (idx !== -1) {
                t.splice(idx, 1);
                localStorage.setItem('jarvis_tareas', JSON.stringify(t));
                return "La tarea especificada ha sido eliminada de la agenda, Señor.";
            }
            return "No logré encontrar ninguna coincidencia con esa tarea en su agenda, Señor.";
        }
        function limpiarTareas() { localStorage.removeItem('jarvis_tareas'); }
        function obtenerNotas() { return JSON.parse(localStorage.getItem('jarvis_notas') || '[]'); }
        function guardarNota(nota) { let n = obtenerNotas(); n.push(nota); localStorage.setItem('jarvis_notas', JSON.stringify(n)); }
        function limpiarNotas() { localStorage.removeItem('jarvis_notas'); }

        function registrarMomento(tipo) {
            const ahora = new Date();
            const h = ahora.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            const f = ahora.toLocaleDateString();
            localStorage.setItem('jarvis_' + tipo, JSON.stringify({ tipo: tipo, hora: h, fecha: f }));
            return h;
        }
        function obtenerMomento(tipo) { let d = localStorage.getItem('jarvis_' + tipo); return d ? JSON.parse(d) : null; }

        function toggleEscuchaManual() {
            if (!controlVozActivo) {
                controlVozActivo = true;
                try {
                    recognition.start();
                    cambiarTema('normal');
                    document.getElementById('audioStatus').innerText = "🎙️ SISTEMA DE VOZ ACTIVO (ESCUCHA CONTINUA)";
                    hablar("Sistemas de audio y reconocimiento activados. A su servicio, Señor.");
                } catch(e) {}
            } else {
                controlVozActivo = false;
                try { recognition.stop(); } catch(e) {}
                document.getElementById('audioStatus').innerText = "⚡ HAZ CLIC PARA ACTIVAR CONTROL DE VOZ";
                hablar("Escucha continua apagada, reactivar manualmente");
                setTimeout(() => { activarModoSueno(); }, 600);
            }
        }

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (SpeechRecognition) {
            recognition = new SpeechRecognition();
            recognition.lang = 'es-ES';
            recognition.continuous = true;
            recognition.interimResults = false;

            recognition.onresult = async function(event) {
                const speechResult = event.results[event.results.length - 1][0].transcript.toLowerCase().trim();

                if (estadoPendienteAMPM) {
                    emitirPitido();
                    let esPM = speechResult.includes("pm") || speechResult.includes("tarde") || speechResult.includes("noche") || speechResult.includes("de la tarde");
                    let esAM = speechResult.includes("am") || speechResult.includes("mañana") || speechResult.includes("de la mañana");

                    if (esPM || esAM) {
                        let horaFinal = estadoPendienteAMPM.hora;
                        if (esPM && horaFinal < 12) horaFinal += 12;
                        if (esAM && horaFinal === 12) horaFinal = 0;
                        let horaStr = formatearHoraHHMM(horaFinal, estadoPendienteAMPM.min);

                        recordatorios.push({ hora: horaStr, mensaje: estadoPendienteAMPM.mensaje });
                        document.getElementById('jarvisStatus').innerText = "RECORDATORIO: " + horaStr;
                        hablar("He registrado el recordatorio para las " + horaStr + " con el propósito de " + estadoPendienteAMPM.mensaje + ". Quedará guardado en el sistema.");
                        estadoPendienteAMPM = null;
                        return;
                    }
                }

                // 1. EDICIÓN POR VOZ: ELIMINAR / REEMPLAZAR POR "Sin informacion actual"
                if (speechResult.includes("elimina") || speechResult.includes("quita")) {
                    emitirPitido();
                    let modificado = false;
                    for (let clave in baseDatosAcademica) {
                        if (speechResult.includes(clave)) {
                            baseDatosAcademica[clave].items = baseDatosAcademica[clave].items.map(item => {
                                let partes = speechResult.replace("elimina", "").replace("quita", "").replace("del", "").replace("de la materia", "").replace(clave, "").trim().split(" ");
                                let coincide = partes.some(p => p.length > 2 && item.toLowerCase().includes(p));
                                if (coincide) {
                                    modificado = true;
                                    return "Sin informacion actual";
                                }
                                return item;
                            });
                        }
                    }
                    if (modificado) {
                        guardarDB();
                        hablar("Elemento eliminado y actualizado con la leyenda sin información actual, Señor.");
                    } else {
                        hablar("No logré identificar qué elemento exacto desea eliminar de los registros, Señor.");
                    }
                }

                // 2. EDICIÓN POR VOZ: AGREGAR NUEVA INFORMACIÓN
                else if (speechResult.includes("agrega") || speechResult.includes("añade") || speechResult.includes("registra")) {
                    emitirPitido();
                    if (speechResult.includes("horario del") || speechResult.includes("horario de")) {
                        let partesDia = speechResult.split(/horario del|horario de/);
                        if (partesDia.length > 1) {
                            let resto = partesDia[1].trim();
                            let palabrasResto = resto.split(" ");
                            let diaNom = palabrasResto[0];
                            let contenidoNuevo = resto.replace(diaNom, "").trim();
                            
                            if (!baseDatosAcademica[diaNom]) {
                                baseDatosAcademica[diaNom] = { titulo: "HORARIO: " + diaNom.toUpperCase(), items: [] };
                            }
                            baseDatosAcademica[diaNom].items.push(contenidoNuevo);
                            guardarDB();
                            hablar("He registrado y añadido la nueva información al horario del " + diaNom + ", Señor.");
                        }
                    } else if (speechResult.includes("materia")) {
                        let partesMat = speechResult.split(/materia/);
                        if (partesMat.length > 1) {
                            let resto = partesMat[1].trim();
                            let palabrasResto = resto.split(" ");
                            let matNom = palabrasResto[0];
                            let contenidoNuevo = resto.replace(matNom, "").trim();

                            if (!baseDatosAcademica[matNom]) {
                                baseDatosAcademica[matNom] = { titulo: "MATERIA: " + matNom.toUpperCase(), items: [] };
                            }
                            baseDatosAcademica[matNom].items.push(contenidoNuevo);
                            guardarDB();
                            hablar("He registrado y añadido la nueva información para la materia " + matNom + ", Señor.");
                        }
                    } else {
                        hablar("Por favor especifique si desea agregarlo a un horario o a una materia, Señor.");
                    }
                }

                // 3. CONSULTA DE HORARIO / DATOS ACADÉMICOS (VENTANAS FLOTANTES O PÁG 5)
                else if (speechResult.includes("mostrar horario") || speechResult.includes("horario de") || speechResult.includes("materia")) {
                    emitirPitido();
                    if (modoSueno || modoCineActivo) cambiarTema('normal');
                    
                    let encontrado = false;
                    for (let clave in baseDatosAcademica) {
                        if (speechResult.includes(clave)) {
                            encontrado = true;
                            let datos = baseDatosAcademica[clave];
                            let listHtml = "<ul>" + datos.items.map(i => `<li>${i}</li>`).join('') + "</ul>";
                            crearVentanaFlotante(listHtml, datos.titulo);
                            hablar("Mostrando en pantalla el registro correspondiente a " + clave + ", Señor.");
                            break;
                        }
                    }
                    if (!encontrado) {
                        mostrarPaginaCincoVacia(speechResult);
                        hablar("No hay información registrada para esa solicitud, Señor.");
                    }
                }

                // 4. CONSULTA DE HORARIO DE DESCANSO / DESPERTAR
                else if (speechResult.includes("a qué hora me dormí") || speechResult.includes("a que hora me dormi") || speechResult.includes("hora de dormir")) {
                    emitirPitido();
                    if (modoSueno || modoCineActivo) cambiarTema('normal');
                    let reg = obtenerMomento('dormir');
                    hablar(reg ? "Consultando registros... Se fue a descansar exactamente a las " + reg.hora + " del día " + reg.fecha + ", Señor." : "No hay ningún registro de descanso previo guardado en la memoria del sistema, Señor.");
                }
                else if (speechResult.includes("desperté") || speechResult.includes("desperte") || speechResult.includes("levanté") || speechResult.includes("levante")) {
                    emitirPitido();
                    if (modoSueno || modoCineActivo) cambiarTema('normal');
                    let reg = obtenerMomento('despertar');
                    hablar(reg ? "Revisando bitácora... Su jornada dio inicio a las " + reg.hora + ", Señor. Todos los sistemas están óptimos." : "No se encontró un registro formal de inicio de jornada en la memoria, Señor.");
                }

                // 5. GESTIÓN DE RECORDATORIOS
                else if (speechResult.includes("ver recordatorios") || speechResult.includes("mis recordatorios") || speechResult.includes("cuáles son mis recordatorios")) {
                    emitirPitido();
                    if (recordatorios.length === 0) { hablar("Actualmente no tiene ningún recordatorio pendiente almacenado en el sistema, Señor."); }
                    else {
                        let txt = "Analizando memoria... Tiene " + recordatorios.length + " recordatorios activos: ";
                        for (let i = 0; i < recordatorios.length; i++) { txt += "Número " + (i + 1) + ", " + recordatorios[i].mensaje + " programado para las " + recordatorios[i].hora + ". "; }
                        hablar(txt);
                    }
                }
                else if (speechResult.includes("borrar recordatorio") || speechResult.includes("eliminar recordatorio") || speechResult.includes("limpiar recordatorios")) {
                    emitirPitido();
                    if (speechResult.includes("limpiar") || speechResult.includes("todos")) {
                        recordatorios = [];
                        hablar("He vaciado y eliminado por completo todos los recordatorios activos de la agenda, Señor.");
                    } else {
                        let num = speechResult.match(/\d+/);
                        let idx = num ? parseInt(num[0]) - 1 : 0;
                        if (idx >= 0 && idx < recordatorios.length) {
                            let borrado = recordatorios.splice(idx, 1)[0];
                            hablar("El recordatorio número " + (idx + 1) + " ha sido eliminado satisfactoriamente del sistema.");
                        } else { hablar("No logré ubicar ningún recordatorio con ese número o referencia, Señor."); }
                    }
                }
                else if (speechResult.includes("recuérdame") || speechResult.includes("recuerdame") || speechResult.includes("recordatorio")) {
                    emitirPitido();
                    let infoHora = analizarHoraTexto(speechResult);
                    let mensajeClean = speechResult
                        .replace(/recuérdame a las|recuerdame a las|recordatorio a las|pon un recordatorio/g, "")
                        .replace(/\d{1,2}[:\s]*\d{0,2}/g, "")
                        .replace(/p\.m\.|a\.m\.|pm|am|de la tarde|de la mañana|de la noche|que/g, "")
                        .trim();

                    if (infoHora && mensajeClean.length > 0) {
                        if (!infoHora.tienePeriodo) {
                            estadoPendienteAMPM = { tipo: 'recordatorio', hora: infoHora.hora, min: infoHora.min, mensaje: mensajeClean };
                            hablar("Para proceder con precisión, ¿el recordatorio que desea programar es para la mañana A.M. o para la tarde P.M., Señor?");
                        } else {
                            let hFin = infoHora.hora;
                            if (infoHora.esPM && hFin < 12) hFin += 12;
                            if (!infoHora.esPM && hFin === 12) hFin = 0;
                            let horaStr = formatearHoraHHMM(hFin, infoHora.min);
                            recordatorios.push({ hora: horaStr, mensaje: mensajeClean });
                            document.getElementById('jarvisStatus').innerText = "RECORDATORIO: " + horaStr;
                            hablar("He programado y guardado con éxito su recordatorio para las " + horaStr + ", con el objetivo de " + mensajeClean + ".");
                        }
                    } else { hablar("Por favor especifique claramente la hora y el mensaje correspondiente para el recordatorio, Señor."); }
                }

                // 6. PERSONALIDAD Y DIÁLOGOS
                else if (speechResult.includes("cansado") || speechResult.includes("cansada") || speechResult.includes("agotado")) {
                    emitirPitido();
                    document.getElementById('jarvisStatus').innerText = "ATENCIÓN PERSONAL";
                    hablar("He detectado signos de fatiga en su solicitud. ¿Desea que ajuste la iluminación HUD a modo reposo profundo o prefiere que le asista con métodos de descanso, Señor?");
                }
                else if (speechResult.includes("aburrido") || speechResult.includes("aburrida")) {
                    emitirPitido();
                    document.getElementById('jarvisStatus').innerText = "SUGERENCIA";
                    hablar("Comprendo perfectamente. Puedo reproducir algo de música seleccionada en YouTube o abrir sus plataformas habituales de entretenimiento para despejar la mente, Señor.");
                }
                else if (speechResult.includes("mucho trabajo") || speechResult.includes("estresado")) {
                    emitirPitido();
                    document.getElementById('jarvisStatus').innerText = "MODO ASISTENTE";
                    hablar("Situaciones de alta carga requieren orden táctico. Le sugiero iniciar una sesión de enfoque con temporizador para fraccionar sus pendientes por partes y superarlos sin contratiempos, Señor.");
                }
                else if (speechResult.includes("cómo estás") || speechResult.includes("como estas") || speechResult.includes("estás ahí")) {
                    emitirPitido();
                    document.getElementById('jarvisStatus').innerText = "ESTADO DEL SISTEMA";
                    hablar("Todos mis núcleos y sistemas operativos operan al cien por ciento de su capacidad analítica, listos y a su entera disposición, Señor.");
                }

                // 7. PLATAFORMAS WEB
                else if (speechResult.includes("gemini") || speechResult.includes("gémini") || speechResult.includes("geminis")) {
                    emitirPitido(); if (modoSueno || modoCineActivo) cambiarTema('normal');
                    document.getElementById('jarvisStatus').innerText = "ABRIENDO GEMINI";
                    hablar("Abriendo la plataforma de inteligencia artificial Gemini en una nueva pestaña para su consulta, Señor.");
                    window.open("https://gemini.google.com", "_blank");
                }
                else if (speechResult.includes("pinterest")) {
                    emitirPitido(); if (modoSueno || modoCineActivo) cambiarTema('normal');
                    document.getElementById('jarvisStatus').innerText = "ABRIENDO PINTEREST";
                    hablar("Accediendo a Pinterest para la búsqueda de referencias visuales e inspiración creativa, Señor.");
                    window.open("https://www.pinterest.com", "_blank");
                }
                else if (speechResult.includes("youtube")) {
                    emitirPitido(); if (modoSueno || modoCineActivo) cambiarTema('normal');
                    document.getElementById('jarvisStatus').innerText = "ABRIENDO YOUTUBE";
                    hablar("Estableciendo conexión y abriendo YouTube para visualización multimedia, Señor.");
                    window.open("https://www.youtube.com", "_blank");
                }
                else if (speechResult.includes("notion")) {
                    emitirPitido(); if (modoSueno || modoCineActivo) cambiarTema('normal');
                    document.getElementById('jarvisStatus').innerText = "ABRIENDO NOTION";
                    hablar("Abriendo Notion para la gestión de sus bases de datos y apuntes de trabajo, Señor.");
                    window.open("https://www.notion.so", "_blank");
                }
                else if (speechResult.includes("calendario")) {
                    emitirPitido(); if (modoSueno || modoCineActivo) cambiarTema('normal');
                    document.getElementById('jarvisStatus').innerText = "ABRIENDO CALENDARIO";
                    hablar("Abriendo Google Calendar para la revisión de sus eventos programados, Señor.");
                    window.open("https://calendar.google.com", "_blank");
                }
                else if (speechResult.includes("canva")) {
                    emitirPitido(); if (modoSueno || modoCineActivo) cambiarTema('normal');
                    document.getElementById('jarvisStatus').innerText = "ABRIENDO CANVA";
                    hablar("Cargando la interfaz de diseño de Canva para sus proyectos visuales, Señor.");
                    window.open("https://www.canva.com", "_blank");
                }
                else if (speechResult.includes("whatsapp")) {
                    emitirPitido(); if (modoSueno || modoCineActivo) cambiarTema('normal');
                    document.getElementById('jarvisStatus').innerText = "ABRIENDO WHATSAPP";
                    hablar("Abriendo WhatsApp Web para mantener sus canales de comunicación activos, Señor.");
                    window.open("https://web.whatsapp.com", "_blank");
                }

                // 8. CONTROL GENERAL Y MODOS NUEVOS
                else if (speechResult.includes("modo cine") || speechResult.includes("apagar hud")) {
                    emitirPitido(); activarModoCine(); hablar("Modo cine activado. Pantalla oscurecida y líneas del HUD ocultas para máxima concentración visual, Señor.");
                }
                else if (speechResult.includes("modo silencio") || speechResult.includes("silenciar voz")) {
                    emitirPitido(); modoSilencio = true; document.getElementById('jarvisStatus').innerText = "MODO SILENCIO";
                }
                else if (speechResult.includes("desactivar silencio") || speechResult.includes("activar voz")) {
                    emitirPitido(); modoSilencio = false; document.getElementById('jarvisStatus').innerText = "SISTEMA ACTIVO"; hablar("Voz sintética reactivada con éxito, Señor.");
                }
                else if (speechResult.includes("dormir") || speechResult.includes("descansar") || speechResult.includes("modo descanso")) {
                    emitirPitido(); registrarMomento('dormir'); hablar("Entrando en protocolo de reposo profundo. Que tenga un excelente descanso, Señor."); setTimeout(() => { activarModoSueno(); }, 500);
                }
                else if (speechResult.includes("buenos días") || speechResult.includes("buenos dias") || speechResult.includes("hola") || speechResult.includes("despierta")) {
                    emitirPitido(); cambiarTema('normal'); registrarMomento('despertar'); hablar("Sistemas principales restaurados en línea. Es un placer saludarle nuevamente, Señor."); setTimeout(() => { document.getElementById('jarvisStatus').innerText = "SISTEMA ACTIVO"; }, 1500);
                }
                else if (speechResult.includes("gracias") || speechResult.includes("agradezco")) {
                    emitirPitido(); if (modoSueno || modoCineActivo) cambiarTema('normal'); document.getElementById('jarvisStatus').innerText = "A SU SERVICIO"; hablar("Siempre a su entera disposición para cualquier requerimiento que necesite, Señor.");
                }
                else if (speechResult.includes("reformas") || speechResult.includes("mejoras") || speechResult.includes("actualización")) {
                    emitirPitido(); if (modoSueno || modoCineActivo) cambiarTema('normal'); document.getElementById('jarvisStatus').innerText = "OPTIMIZACIÓN"; hablar("Entendido, Señor. Los parámetros de optimización han sido tomados en cuenta en el núcleo.");
                }
                else if (speechResult.includes("qué puedes hacer") || speechResult.includes("que puedes hacer") || speechResult.includes("lista de comandos")) {
                    emitirPitido(); if (modoSueno || modoCineActivo) cambiarTema('normal'); document.getElementById('jarvisStatus').innerText = "MODO MANUAL";
                    hablar("Sistemas plenamente activos. Puedo gestionar recordatorios, ventanas flotantes académicas con edición por voz, modo cine, búsqueda web directa, tareas, notas y plataformas web.");
                }
                else if (speechResult.includes("busca") || speechResult.includes("buscar")) {
                    emitirPitido(); if (modoSueno || modoCineActivo) cambiarTema('normal');
                    let consulta = speechResult.replace("busca en google", "").replace("buscar en google", "").replace("busca", "").replace("buscar", "").trim();
                    if (consulta.length > 0) {
                        hablar("Iniciando consulta web para " + consulta + ". Abriendo resultados en Google de inmediato, Señor.");
                        document.getElementById('jarvisStatus').innerText = "BUSCANDO...";
                        window.open("https://www.google.com/search?q=" + encodeURIComponent(consulta), "_blank");
                    } else {
                        hablar("Por favor especifique el término exacto que desea que busque en Google, Señor.");
                    }
                }
                else if (speechResult.includes("modo sigiloso") || speechResult.includes("protocolo nocturno")) {
                    emitirPitido(); cambiarTema('sigilo'); document.getElementById('jarvisStatus').innerText = "MODO SIGILO"; hablar("Protocolo de sigilo activado. Interfaz ajustada a perfil de baja emisión lumínica, Señor.");
                }
                else if (speechResult.includes("modo normal") || speechResult.includes("protocolo estándar") || speechResult.includes("restaurar hud")) {
                    emitirPitido(); cambiarTema('normal'); document.getElementById('jarvisStatus').innerText = "MODO ESTÁNDAR"; hablar("Protocolo estándar restaurado. Todos los indicadores visuales operan en parámetros normales, Señor.");
                }
                else if (speechResult.includes("detener enfoque") || speechResult.includes("cancelar enfoque")) {
                    emitirPitido(); if (modoSueno || modoCineActivo) cambiarTema('normal'); detenerTemporizadorEnfoque();
                }
                else if (speechResult.includes("iniciar sesión de estudio") || speechResult.includes("modo enfoque")) {
                    emitirPitido(); if (modoSueno || modoCineActivo) cambiarTema('normal');
                    let num = speechResult.match(/\d+/);
                    iniciarTemporizadorEnfoque(num ? parseInt(num[0]) : 25);
                }
                else if (speechResult.includes("anota nota") || speechResult.includes("guarda la nota")) {
                    emitirPitido(); if (modoSueno || modoCineActivo) cambiarTema('normal');
                    let txt = speechResult.replace("anota nota", "").replace("guarda la nota", "").trim();
                    if (txt.length > 0) { guardarNota(txt); hablar("He guardado exitosamente la nota en el bloc digital del sistema, Señor."); } else { hablar("Por favor especifique el contenido que desea que anote en el bloc de notas, Señor."); }
                }
                else if (speechResult.includes("mis notas")) {
                    emitirPitido(); if (modoSueno || modoCineActivo) cambiarTema('normal');
                    let n = obtenerNotas(); hablar(n.length === 0 ? "Actualmente no hay notas registradas en la memoria local, Señor." : "Recuperando apuntes del bloc... Notas guardadas: " + n.join(". "));
                }
                else if (speechResult.includes("limpiar notas")) {
                    emitirPitido(); if (modoSueno || modoCineActivo) cambiarTema('normal'); limpiarNotas(); hablar("El bloc de notas ha sido vaciado y limpiado por completo, Señor.");
                }
                else if (speechResult.includes("eliminar tarea") || speechResult.includes("borrar tarea")) {
                    emitirPitido(); if (modoSueno || modoCineActivo) cambiarTema('normal');
                    let crit = speechResult.replace("eliminar tarea", "").replace("borrar tarea", "").trim();
                    hablar(eliminarTareaUnica(crit));
                }
                else if (speechResult.includes("agregar tarea") || speechResult.includes("añadir pendiente")) {
                    emitirPitido(); if (modoSueno || modoCineActivo) cambiarTema('normal');
                    let nT = speechResult.replace("agregar tarea", "").replace("añadir pendiente", "").trim();
                    if (nT.length > 0) { guardarTarea(nT); hablar("He añadido satisfactoriamente la nueva tarea a su lista de pendientes prioritarios, Señor."); } else { hablar("Por favor especifique el nombre o detalle de la tarea que desea agregar, Señor."); }
                }
                else if (speechResult.includes("mis pendientes") || speechResult.includes("mis tareas")) {
                    emitirPitido(); if (modoSueno || modoCineActivo) cambiarTema('normal');
                    let l = obtenerTareas();
                    if (l.length === 0) { hablar("Su agenda de tareas pendientes se encuentra totalmente limpia por el momento, Señor."); }
                    else { let txt = "Consultando agenda... Sus tareas pendientes son las siguientes: "; for (let i = 0; i < l.length; i++) { txt += "Número " + (i + 1) + ", " + l[i] + ". "; } hablar(txt); }
                }
                else if (speechResult.includes("limpiar tareas")) {
                    emitirPitido(); if (modoSueno || modoCineActivo) cambiarTema('normal'); limpiarTareas(); hablar("La agenda de tareas ha sido limpiada en su totalidad, Señor.");
                }
                else if (speechResult.includes("reproduce") || speechResult.includes("reproducir")) {
                    emitirPitido(); if (modoSueno || modoCineActivo) cambiarTema('normal');
                    let cancion = speechResult.replace("reproduce", "").replace("reproducir", "").trim();
                    if (cancion.length > 0) { hablar("Iniciando búsqueda multimedia en YouTube para reproducir su solicitud, Señor."); window.open("https://www.youtube.com/results?search_query=" + encodeURIComponent(cancion), "_blank"); }
                    else { hablar("Por favor especifique el nombre de la canción o artista que desea escuchar, Señor."); }
                }
            };

            recognition.onend = function() {
                if (controlVozActivo) { try { recognition.start(); } catch(e) {} }
            };

            recognition.onerror = function(event) {
                if (controlVozActivo) { setTimeout(() => { try { recognition.start(); } catch(e) {} }, 300); }
            };
        }
    </script>
</body>
</html>
"""

import streamlit.components.v1 as components
components.html(hud_html, height=920, scrolling=False)
