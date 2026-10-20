import streamlit as st
import json
import os

st.set_page_config(
    page_title="JARVIS HUD",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilo para centrado absoluto y eliminación de márgenes superiores
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
        * {
            box-sizing: border-box;
        }
        html, body {
            background-color: #010a17;
            margin: 0;
            padding: 0;
            width: 100vw;
            height: 100vh;
            overflow: hidden;
            display: flex;
            justify-content: center;
            align-items: center;
            font-family: 'Consolas', monospace;
            transition: background-color 1s ease;
        }
        .hud-container {
            position: relative;
            width: 100vw;
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        canvas {
            position: absolute;
            top: 0;
            left: 0;
            transition: opacity 1s ease;
        }
        .core-text {
            position: absolute;
            text-align: center;
            color: #00f3ff;
            z-index: 10;
            pointer-events: none;
        }
        .core-text h1 {
            margin: 0;
            font-size: 38px;
            letter-spacing: 8px;
            color: #ffffff;
            text-shadow: 0 0 20px #00f3ff, 0 0 40px #00f3ff;
            font-weight: 800;
            transition: color 1s ease, text-shadow 1s ease;
        }
        .core-text p {
            margin: 8px 0 0 0;
            font-size: 11px;
            color: #38bdf8;
            letter-spacing: 4px;
            text-transform: uppercase;
            transition: color 1s ease;
        }
        .status-bar {
            position: absolute;
            bottom: 25px;
            color: #0ea5e9;
            font-size: 11px;
            letter-spacing: 3px;
            text-transform: uppercase;
            background: rgba(1, 10, 23, 0.85);
            padding: 8px 20px;
            border: 1px solid #00f3ff44;
            border-radius: 4px;
            box-shadow: 0 0 12px rgba(0, 243, 255, 0.25);
            cursor: pointer;
            transition: opacity 1s ease, border-color 1s ease, color 1s ease;
            z-index: 20;
        }
        .diagnostic-panel {
            position: absolute;
            top: 20px;
            right: 25px;
            background: rgba(1, 10, 23, 0.85);
            border: 1px solid #00f3ff55;
            border-radius: 6px;
            padding: 10px 16px;
            color: #00f3ff;
            font-size: 11px;
            letter-spacing: 2px;
            box-shadow: 0 0 15px rgba(0, 243, 255, 0.2);
            z-index: 20;
            pointer-events: none;
            text-align: right;
        }
        .diagnostic-panel .clock {
            font-size: 18px;
            font-weight: bold;
            color: #ffffff;
            text-shadow: 0 0 8px #00f3ff;
            margin-bottom: 2px;
        }
        .diagnostic-panel .sys-info {
            font-size: 10px;
            color: #38bdf8;
        }
    </style>
</head>
<body>
    <div class="hud-container">
        <canvas id="hudCanvas"></canvas>
        <div class="core-text">
            <h1 id="jarvisTitle">J.A.R.V.I.S</h1>
            <p id="jarvisStatus">SISTEMA EN LÍNEA</p>
        </div>
        <div class="diagnostic-panel" id="diagPanel">
            <div class="clock" id="hudClock">00:00:00</div>
            <div class="sys-info">CPU: 4.2% | MEM: 1.4GB</div>
            <div class="sys-info" id="modeInfo">MODO: ESTÁNDAR</div>
        </div>
        <div class="status-bar" id="audioStatus">⚡ HAZ CLIC PARA ACTIVAR CONTROL DE VOZ</div>
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

        setInterval(() => {
            const now = new Date();
            document.getElementById('hudClock').innerText = now.toLocaleTimeString();
        }, 1000);

        let angleMain = 0;
        let angleInner = 0;
        let angleOuter = 0;
        let modoSueno = false;
        let modoSilencio = false;
        let pulseTime = 0;

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
            canvas.style.opacity = "1";
            document.body.style.backgroundColor = "#010a17";
            document.getElementById('audioStatus').style.opacity = "1";
            document.getElementById('diagPanel').style.opacity = "1";

            if (modo === 'sigilo') {
                theme.primary = '#ff2a2a';
                theme.secondary = '#f87171';
                theme.darkLine = '#991b1b';
                theme.dimLine = 'rgba(80, 10, 10, 0.35)';
                theme.glow = 'rgba(255, 42, 42, 0.9)';
                document.getElementById('jarvisTitle').style.textShadow = "0 0 20px #ff2a2a, 0 0 40px #ff2a2a";
                document.getElementById('jarvisStatus').style.color = "#f87171";
                document.getElementById('modeInfo').innerText = "MODO: SIGILO";
            } else if (modo === 'normal') {
                theme.primary = '#00f3ff';
                theme.secondary = '#38bdf8';
                theme.darkLine = '#0284c7';
                theme.dimLine = 'rgba(2, 40, 80, 0.35)';
                theme.glow = 'rgba(0, 243, 255, 0.9)';
                document.getElementById('jarvisTitle').style.textShadow = "0 0 20px #00f3ff, 0 0 40px #00f3ff";
                document.getElementById('jarvisStatus').style.color = "#38bdf8";
                document.getElementById('modeInfo').innerText = "MODO: ESTÁNDAR";
            }
        }

        function activarModoSueno() {
            modoSueno = true;
            document.body.style.backgroundColor = "#000000";
            canvas.style.opacity = "0.2";
            document.getElementById('audioStatus').style.opacity = "0.3";
            document.getElementById('diagPanel').style.opacity = "0.3";
            theme.primary = '#0284c7';
            theme.secondary = '#0369a1';
            theme.darkLine = '#0c4a6e';
            theme.dimLine = 'rgba(2, 20, 40, 0.15)';
            document.getElementById('jarvisTitle').style.textShadow = "0 0 10px #0284c7";
            document.getElementById('jarvisStatus').style.color = "#0284c7";
            document.getElementById('jarvisStatus').innerText = "REPOSO PROFUNDO";
            document.getElementById('modeInfo').innerText = "MODO: SUEÑO";
        }

        let timerInterval = null;
        let tiempoRestanteSegundos = 0;

        function drawBackgroundGrid() {
            ctx.save();
            ctx.strokeStyle = theme.dimLine;
            ctx.lineWidth = 1;

            for(let x = 0; x < canvas.width; x += 40) {
                ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, canvas.height); ctx.stroke();
            }
            for(let y = 0; y < canvas.height; y += 40) {
                ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(canvas.width, y); ctx.stroke();
            }
            ctx.restore();
        }

        function drawNodeDot(x, y, radius = 4) {
            ctx.beginPath();
            ctx.arc(x, y, radius, 0, Math.PI * 2);
            ctx.fillStyle = theme.primary;
            ctx.shadowBlur = modoSueno ? 3 : 10;
            ctx.shadowColor = theme.primary;
            ctx.fill();
        }

        function drawTargetNode(x, y, size = 26) {
            ctx.save();
            ctx.strokeStyle = theme.primary;
            ctx.lineWidth = 1.8;
            ctx.shadowBlur = modoSueno ? 3 : 10;
            ctx.shadowColor = theme.primary;

            ctx.beginPath(); ctx.arc(x, y, size, 0, Math.PI * 2); ctx.stroke();
            ctx.beginPath(); ctx.arc(x, y, size * 0.65, 0, Math.PI * 2); ctx.strokeStyle = theme.secondary; ctx.stroke();
            ctx.beginPath(); ctx.arc(x, y, size * 0.3, 0, Math.PI * 2); ctx.stroke();
            ctx.beginPath(); ctx.arc(x, y, 3, 0, Math.PI * 2); ctx.fillStyle = theme.primary; ctx.fill();
            ctx.restore();
        }

        function drawPCB(cx, cy) {
            ctx.save();
            ctx.strokeStyle = theme.darkLine;
            ctx.lineWidth = 2;
            ctx.shadowBlur = modoSueno ? 2 : 8;
            ctx.shadowColor = theme.primary;

            let lY1 = cy - 190;
            ctx.beginPath(); ctx.moveTo(0, lY1); ctx.lineTo(cx - 380, lY1); ctx.lineTo(cx - 320, lY1 + 60); ctx.lineTo(cx - 230, lY1 + 60); ctx.stroke();
            drawNodeDot(cx - 380, lY1); drawNodeDot(cx - 230, lY1 + 60);

            let lY2 = cy - 90;
            ctx.beginPath(); ctx.moveTo(0, lY2); ctx.lineTo(cx - 340, lY2); ctx.lineTo(cx - 280, lY2 + 30); ctx.lineTo(cx - 220, lY2 + 30); ctx.stroke();
            drawNodeDot(cx - 340, lY2); drawNodeDot(cx - 220, lY2 + 30);

            let lY3 = cy + 120;
            ctx.beginPath(); ctx.moveTo(0, lY3); ctx.lineTo(cx - 400, lY3); ctx.lineTo(cx - 330, lY3 - 50); ctx.lineTo(cx - 230, lY3 - 50); ctx.stroke();
            drawNodeDot(cx - 400, lY3); drawNodeDot(cx - 230, lY3 - 50);

            let lY4 = cy + 210;
            ctx.beginPath(); ctx.moveTo(0, lY4); ctx.lineTo(cx - 300, lY4); ctx.lineTo(cx - 250, lY4 - 40); ctx.lineTo(cx - 210, lY4 - 40); ctx.stroke();

            ctx.strokeStyle = theme.secondary;
            ctx.strokeRect(50, cy - 230, 120, 48);
            ctx.strokeRect(65, cy - 220, 40, 28);
            drawTargetNode(80, cy + 190, 26);

            let rY1 = cy - 200;
            ctx.beginPath(); ctx.moveTo(canvas.width, rY1); ctx.lineTo(cx + 400, rY1); ctx.lineTo(cx + 330, rY1 + 60); ctx.lineTo(cx + 230, rY1 + 60); ctx.stroke();
            drawNodeDot(cx + 400, rY1); drawNodeDot(cx + 230, rY1 + 60);

            let rY2 = cy - 60;
            ctx.beginPath(); ctx.moveTo(canvas.width, rY2); ctx.lineTo(cx + 350, rY2); ctx.lineTo(cx + 290, rY2 - 30); ctx.lineTo(cx + 230, rY2 - 30); ctx.stroke();
            drawNodeDot(cx + 350, rY2);

            let rY3 = cy + 140;
            ctx.beginPath(); ctx.moveTo(canvas.width, rY3); ctx.lineTo(cx + 380, rY3); ctx.lineTo(cx + 310, rY3 - 60); ctx.lineTo(cx + 220, rY3 - 60); ctx.stroke();
            drawNodeDot(cx + 380, rY3); drawNodeDot(cx + 220, rY3 - 60);

            drawTargetNode(canvas.width - 90, cy - 200, 26);

            ctx.strokeStyle = theme.primary;
            ctx.strokeRect(cx + 290, cy + 20, 75, 95);
            for(let i = 0; i < 4; i++) {
                ctx.fillStyle = theme.primary;
                ctx.fillRect(cx + 304 + (i * 13), cy + 35, 6, 65);
            }

            let grad = ctx.createLinearGradient(cx - 320, cy, cx + 320, cy);
            grad.addColorStop(0, 'transparent');
            grad.addColorStop(0.5, theme.primary);
            grad.addColorStop(1, 'transparent');
            ctx.strokeStyle = grad;
            ctx.lineWidth = 1.5;
            ctx.beginPath(); ctx.moveTo(cx - 320, cy); ctx.lineTo(cx + 320, cy); ctx.stroke();

            ctx.restore();
        }

        function drawHUD() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            let cx = canvas.width / 2;
            let cy = canvas.height / 2;

            drawBackgroundGrid();
            drawPCB(cx, cy);

            let speedMultiplier = modoSueno ? 0.2 : 1.0;
            angleMain += 0.004 * speedMultiplier;
            angleInner -= 0.006 * speedMultiplier;
            angleOuter += 0.002 * speedMultiplier;

            ctx.save();
            ctx.translate(cx, cy);
            ctx.rotate(angleOuter);
            ctx.strokeStyle = theme.primary;
            ctx.lineWidth = 3;
            ctx.shadowBlur = modoSueno ? 5 : 15;
            ctx.shadowColor = theme.primary;

            ctx.beginPath(); ctx.arc(0, 0, 235, 0, Math.PI * 1.35); ctx.stroke();
            ctx.beginPath(); ctx.arc(0, 0, 235, Math.PI * 1.45, Math.PI * 1.85); ctx.stroke();
            ctx.restore();

            ctx.save();
            ctx.translate(cx, cy);
            ctx.rotate(-angleOuter * 1.5);
            ctx.fillStyle = theme.secondary;
            for (let i = 0; i < 18; i++) {
                let angle = (i * 7.5) * Math.PI / 180 + Math.PI * 0.2;
                let x = Math.cos(angle) * 215;
                let y = Math.sin(angle) * 215;
                ctx.fillRect(x, y, 4, 4);
            }
            ctx.restore();

            ctx.save();
            ctx.translate(cx, cy);
            ctx.rotate(angleInner);
            ctx.strokeStyle = theme.secondary;
            ctx.lineWidth = 1.5;
            for (let i = 0; i < 90; i++) {
                ctx.beginPath();
                let angle = (i * 4) * Math.PI / 180;
                let len = (i % 5 === 0) ? 12 : 6;
                let x1 = Math.cos(angle) * 195;
                let y1 = Math.sin(angle) * 195;
                let x2 = Math.cos(angle) * (195 - len);
                let y2 = Math.sin(angle) * (195 - len);
                ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.stroke();
            }
            ctx.restore();

            ctx.save();
            ctx.translate(cx, cy);
            ctx.rotate(angleMain * 0.8);
            ctx.fillStyle = theme.primary;
            for (let i = 0; i < 24; i++) {
                let angle = (i * 3.5) * Math.PI / 180 + Math.PI * 0.75;
                let x = Math.cos(angle) * 172;
                let y = Math.sin(angle) * 172;
                ctx.fillRect(x, y, 5, 10);
            }
            ctx.restore();

            ctx.save();
            ctx.translate(cx, cy);
            ctx.rotate(-angleMain * 0.5);
            ctx.fillStyle = theme.secondary;
            ctx.font = '11px Consolas, monospace';
            let zerosUpper = "0000000000";
            for (let i = 0; i < zerosUpper.length; i++) {
                let angle = (i * 6) * Math.PI / 180 - Math.PI * 0.4;
                let x = Math.cos(angle) * 152;
                let y = Math.sin(angle) * 152;
                ctx.fillText(zerosUpper[i], x, y);
            }
            let zerosLower = "0000000000000";
            for (let i = 0; i < zerosLower.length; i++) {
                let angle = (i * 6) * Math.PI / 180 + Math.PI * 0.6;
                let x = Math.cos(angle) * 152;
                let y = Math.sin(angle) * 152;
                ctx.fillText(zerosLower[i], x, y);
            }
            ctx.restore();

            pulseTime += 0.02;
            let pulseGlow = modoSueno ? (Math.sin(pulseTime) * 8 + 12) : 20;

            ctx.save();
            ctx.beginPath();
            ctx.arc(cx, cy, 118, 0, Math.PI * 2);
            ctx.fillStyle = modoSueno ? 'rgba(0, 0, 0, 0.98)' : 'rgba(1, 10, 23, 0.95)';
            ctx.fill();
            ctx.strokeStyle = theme.primary;
            ctx.lineWidth = 3.5;
            ctx.shadowBlur = pulseGlow;
            ctx.shadowColor = theme.primary;
            ctx.stroke();
            ctx.restore();

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

        function iniciarTemporizadorEnfoque(minutos) {
            cambiarTema('normal');
            if (timerInterval) {
                clearInterval(timerInterval);
                timerInterval = null;
            }
            tiempoRestanteSegundos = minutos * 60;
            hablar("Enfoque activado: " + minutos + " minutos.");

            timerInterval = setInterval(() => {
                if (tiempoRestanteSegundos <= 0) {
                    clearInterval(timerInterval);
                    timerInterval = null;
                    document.getElementById('jarvisStatus').innerText = "TIEMPO FINALIZADO";
                    hablar("Tiempo finalizado.");
                } else {
                    tiempoRestanteSegundos--;
                    let m = Math.floor(tiempoRestanteSegundos / 60);
                    let s = tiempoRestanteSegundos % 60;
                    let mFormato = m < 10 ? "0" + m : m;
                    let sFormato = s < 10 ? "0" + s : s;
                    document.getElementById('jarvisStatus').innerText = "ENFOQUE: " + mFormato + ":" + sFormato;
                }
            }, 1000);
        }

        function detenerTemporizadorEnfoque() {
            if (timerInterval) {
                clearInterval(timerInterval);
                timerInterval = null;
                document.getElementById('jarvisStatus').innerText = "SISTEMA ACTIVO";
                hablar("Sesión cancelada.");
            } else {
                hablar("No hay enfoque activo.");
            }
        }

        function obtenerTareas() {
            return JSON.parse(localStorage.getItem('jarvis_tareas') || '[]');
        }

        function guardarTarea(tarea) {
            let tareas = obtenerTareas();
            tareas.push(tarea);
            localStorage.setItem('jarvis_tareas', JSON.stringify(tareas));
        }

        function eliminarTareaUnica(criterio) {
            let tareas = obtenerTareas();
            if (tareas.length === 0) return { exito: false, mensaje: "No hay tareas registradas." };

            let numero = parseInt(criterio);
            if (!isNaN(numero) && numero > 0 && numero <= tareas.length) {
                let borrada = tareas.splice(numero - 1, 1)[0];
                localStorage.setItem('jarvis_tareas', JSON.stringify(tareas));
                return { exito: true, mensaje: "Tarea " + numero + " eliminada." };
            }

            let indiceEncontrado = tareas.findIndex(t => t.toLowerCase().includes(criterio.toLowerCase()));
            if (indiceEncontrado !== -1) {
                let borrada = tareas.splice(indiceEncontrado, 1)[0];
                localStorage.setItem('jarvis_tareas', JSON.stringify(tareas));
                return { exito: true, mensaje: "Tarea eliminada." };
            }

            return { exito: false, mensaje: "No encontré esa tarea." };
        }

        function limpiarTareas() {
            localStorage.removeItem('jarvis_tareas');
        }

        function obtenerNotas() {
            return JSON.parse(localStorage.getItem('jarvis_notas') || '[]');
        }

        function guardarNota(nota) {
            let notas = obtenerNotas();
            notas.push(nota);
            localStorage.setItem('jarvis_notas', JSON.stringify(notas));
        }

        function limpiarNotas() {
            localStorage.removeItem('jarvis_notas');
        }

        function registrarMomento(tipo) {
            const ahora = new Date();
            const horaFormateada = ahora.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            const fechaFormateada = ahora.toLocaleDateString();
            const registro = { tipo: tipo, hora: horaFormateada, fecha: fechaFormateada };
            localStorage.setItem('jarvis_' + tipo, JSON.stringify(registro));
            return horaFormateada;
        }

        function obtenerMomento(tipo) {
            let data = localStorage.getItem('jarvis_' + tipo);
            return data ? JSON.parse(data) : null;
        }

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (SpeechRecognition) {
            const recognition = new SpeechRecognition();
            recognition.lang = 'es-ES';
            recognition.continuous = true;
            recognition.interimResults = false;
            let activadoPorUsuario = false;

            recognition.onresult = async function(event) {
                const speechResult = event.results[event.results.length - 1][0].transcript.toLowerCase().trim();

                // 1. MODO SILENCIO
                if (speechResult.includes("modo silencio") || speechResult.includes("silenciar voz")) {
                    emitirPitido();
                    modoSilencio = true;
                    document.getElementById('jarvisStatus').innerText = "MODO SILENCIO";
                }
                else if (speechResult.includes("desactivar silencio") || speechResult.includes("activar voz")) {
                    emitirPitido();
                    modoSilencio = false;
                    document.getElementById('jarvisStatus').innerText = "SISTEMA ACTIVO";
                    hablar("Voz reactivada.");
                }

                // 2. MODO REPOSO / SUEÑO
                else if (speechResult.includes("dormir") || speechResult.includes("descansar") || speechResult.includes("modo descanso") || speechResult.includes("ir a dormir")) {
                    emitirPitido();
                    let hora = registrarMomento('dormir');
                    hablar("Entrando en reposo.");
                    setTimeout(() => { activarModoSueno(); }, 500);
                }

                // 3. ACTIVACIÓN / DESPERTAR
                else if (speechResult.includes("buenos días") || speechResult.includes("buenos dias") || speechResult.includes("buenas noches") || speechResult.includes("hola") || speechResult.includes("despierta")) {
                    emitirPitido();
                    cambiarTema('normal');
                    let hora = registrarMomento('despertar');
                    hablar("Sistemas en línea.");
                    setTimeout(() => { document.getElementById('jarvisStatus').innerText = "SISTEMA ACTIVO"; }, 1500);
                }

                // 4. AGRADECIMIENTO
                else if (speechResult.includes("gracias") || speechResult.includes("agradezco")) {
                    emitirPitido();
                    if (modoSueno) cambiarTema('normal');
                    document.getElementById('jarvisStatus').innerText = "A SU SERVICIO";
                    hablar("A su servicio.");
                }

                // 5. REFORMAS Y MEJORAS
                else if (speechResult.includes("reformas") || speechResult.includes("mejoras") || speechResult.includes("actualización")) {
                    emitirPitido();
                    if (modoSueno) cambiarTema('normal');
                    document.getElementById('jarvisStatus').innerText = "OPTIMIZACIÓN";
                    hablar("Entendido, Señor.");
                }

                // 6. MANUAL DE COMANDOS
                else if (speechResult.includes("qué puedes hacer") || speechResult.includes("que puedes hacer") || speechResult.includes("lista de comandos")) {
                    emitirPitido();
                    if (modoSueno) cambiarTema('normal');
                    document.getElementById('jarvisStatus').innerText = "MODO MANUAL";
                    hablar("Sistemas activos. Puedo registrar jornadas, gestionar tareas y notas, activar temporizadores, reproducir música, cambiar modos visuales, activar modo silencio, abrir plataformas y buscar en Google.");
                }

                // 7. BÚSQUEDA EN GOOGLE
                else if (speechResult.includes("busca") || speechResult.includes("buscar")) {
                    emitirPitido();
                    if (modoSueno) cambiarTema('normal');
                    let consulta = speechResult
                        .replace(/jarvis|yarbi|yarvis|jarbi|arvis/g, "")
                        .replace("busca en google", "")
                        .replace("buscar en google", "")
                        .replace("busca", "")
                        .replace("buscar", "")
                        .trim();
                    if (consulta.length > 0) {
                        hablar("Buscando...");
                        document.getElementById('jarvisStatus').innerText = "BUSCANDO...";
                        window.open("https://www.google.com/search?q=" + encodeURIComponent(consulta), "_blank");
                    } else {
                        hablar("Especifique qué buscar.");
                    }
                }

                // 8. CONSULTAS DE HORARIO
                else if (speechResult.includes("desperté") || speechResult.includes("desperte") || speechResult.includes("levanté")) {
                    emitirPitido();
                    if (modoSueno) cambiarTema('normal');
                    let reg = obtenerMomento('despertar');
                    hablar(reg ? "Inició a las " + reg.hora : "Sin registro.");
                }
                else if (speechResult.includes("a qué hora me dormí") || speechResult.includes("a que hora me dormi")) {
                    emitirPitido();
                    if (modoSueno) cambiarTema('normal');
                    let reg = obtenerMomento('dormir');
                    hablar(reg ? "Se fue a descansar a las " + reg.hora : "Sin registro.");
                }

                // 9. MODO VISUAL
                else if (speechResult.includes("modo sigiloso") || speechResult.includes("protocolo nocturno")) {
                    emitirPitido();
                    cambiarTema('sigilo');
                    document.getElementById('jarvisStatus').innerText = "MODO SIGILO";
                    hablar("Modo sigilo.");
                }
                else if (speechResult.includes("modo normal") || speechResult.includes("protocolo estándar")) {
                    emitirPitido();
                    cambiarTema('normal');
                    document.getElementById('jarvisStatus').innerText = "MODO ESTÁNDAR";
                    hablar("Modo estándar.");
                }

                // 10. TEMPORIZADOR
                else if (speechResult.includes("detener enfoque") || speechResult.includes("cancelar enfoque")) {
                    emitirPitido();
                    if (modoSueno) cambiarTema('normal');
                    detenerTemporizadorEnfoque();
                }
                else if (speechResult.includes("iniciar sesión de estudio") || speechResult.includes("modo enfoque")) {
                    emitirPitido();
                    if (modoSueno) cambiarTema('normal');
                    let numeros = speechResult.match(/\d+/);
                    let minutos = numeros ? parseInt(numeros[0]) : 25;
                    iniciarTemporizadorEnfoque(minutos);
                }

                // 11. NOTAS
                else if (speechResult.includes("anota nota") || speechResult.includes("guarda la nota")) {
                    emitirPitido();
                    if (modoSueno) cambiarTema('normal');
                    let notaText = speechResult.replace(/jarvis|yarbi|yarvis|jarbi|arvis/g, "").replace("anota nota", "").replace("guarda la nota", "").trim();
                    if (notaText.length > 0) {
                        guardarNota(notaText);
                        hablar("Nota registrada.");
                    } else {
                        hablar("Especifique la nota.");
                    }
                }
                else if (speechResult.includes("mis notas")) {
                    emitirPitido();
                    if (modoSueno) cambiarTema('normal');
                    let notas = obtenerNotas();
                    hablar(notas.length === 0 ? "Sin notas." : "Notas: " + notas.join(". "));
                }
                else if (speechResult.includes("limpiar notas")) {
                    emitirPitido();
                    if (modoSueno) cambiarTema('normal');
                    limpiarNotas();
                    hablar("Notas borradas.");
                }

                // 12. TAREAS
                else if (speechResult.includes("eliminar tarea") || speechResult.includes("borrar tarea")) {
                    emitirPitido();
                    if (modoSueno) cambiarTema('normal');
                    let criterio = speechResult.replace(/jarvis|yarbi|yarvis|jarbi|arvis/g, "").replace("eliminar tarea", "").replace("borrar tarea", "").trim();
                    let res = eliminarTareaUnica(criterio);
                    hablar(res.mensaje);
                }
                else if (speechResult.includes("agregar tarea") || speechResult.includes("añadir pendiente")) {
                    emitirPitido();
                    if (modoSueno) cambiarTema('normal');
                    let nuevaTarea = speechResult.replace(/jarvis|yarbi|yarvis|jarbi|arvis/g, "").replace("agregar tarea", "").replace("añadir pendiente", "").trim();
                    if (nuevaTarea.length > 0) {
                        guardarTarea(nuevaTarea);
                        hablar("Tarea anotada.");
                    } else {
                        hablar("Especifique la tarea.");
                    }
                }
                else if (speechResult.includes("mis pendientes") || speechResult.includes("mis tareas")) {
                    emitirPitido();
                    if (modoSueno) cambiarTema('normal');
                    let lista = obtenerTareas();
                    if (lista.length === 0) {
                        hablar("No tiene pendientes.");
                    } else {
                        let txt = "Pendientes: ";
                        for (let i = 0; i < lista.length; i++) { txt += (i + 1) + ", " + lista[i] + ". "; }
                        hablar(txt);
                    }
                }
                else if (speechResult.includes("limpiar tareas")) {
                    emitirPitido();
                    if (modoSueno) cambiarTema('normal');
                    limpiarTareas();
                    hablar("Agenda limpia.");
                }

                // 13. MÚSICA YOUTUBE
                else if (speechResult.includes("reproduce") || speechResult.includes("reproducir")) {
                    emitirPitido();
                    if (modoSueno) cambiarTema('normal');
                    let cancion = speechResult.replace(/jarvis|yarbi|yarvis|jarbi|arvis/g, "").replace("reproduce", "").replace("reproducir", "").trim();
                    if (cancion.length > 0) {
                        hablar("Reproduciendo.");
                        window.open("https://www.youtube.com/results?search_query=" + encodeURIComponent(cancion), "_blank");
                    } else {
                        hablar("Especifique la canción.");
                    }
                }

                // 14. PLATAFORMAS WEB
                else if (speechResult.includes("pinterest")) {
                    emitirPitido();
                    if (modoSueno) cambiarTema('normal');
                    hablar("Abriendo Pinterest.");
                    window.open("https://www.pinterest.com", "_blank");
                }
                else if (speechResult.includes("youtube")) {
                    emitirPitido();
                    if (modoSueno) cambiarTema('normal');
                    hablar("Abriendo YouTube.");
                    window.open("https://www.youtube.com", "_blank");
                }
                else if (speechResult.includes("notion")) {
                    emitirPitido();
                    if (modoSueno) cambiarTema('normal');
                    hablar("Abriendo Notion.");
                    window.open("https://www.notion.so", "_blank");
                }
                else if (speechResult.includes("calendario")) {
                    emitirPitido();
                    if (modoSueno) cambiarTema('normal');
                    hablar("Abriendo Calendario.");
                    window.open("https://calendar.google.com", "_blank");
                }
                else if (speechResult.includes("canva")) {
                    emitirPitido();
                    if (modoSueno) cambiarTema('normal');
                    hablar("Abriendo Canva.");
                    window.open("https://www.canva.com", "_blank");
                }
                else if (speechResult.includes("whatsapp")) {
                    emitirPitido();
                    if (modoSueno) cambiarTema('normal');
                    hablar("Abriendo WhatsApp.");
                    window.open("https://web.whatsapp.com", "_blank");
                }
                else if (speechResult.includes("gemini")) {
                    emitirPitido();
                    if (modoSueno) cambiarTema('normal');
                    hablar("Abriendo Gemini.");
                    window.open("https://gemini.google.com", "_blank");
                }
            };

            recognition.onend = function() {
                if (activadoPorUsuario) {
                    try { recognition.start(); } catch(e) {}
                }
            };

            recognition.onerror = function(event) {
                if (activadoPorUsuario) {
                    setTimeout(() => { try { recognition.start(); } catch(e) {} }, 300);
                }
            };

            window.addEventListener('click', () => {
                activadoPorUsuario = true;
                try {
                    recognition.start();
                    document.getElementById('audioStatus').innerText = "🎙️ SISTEMA DE VOZ ACTIVO (ESCUCHA CONTINUA)";
                } catch(e) {}
            });
        }
    </script>
</body>
</html>
"""

import streamlit.components.v1 as components
components.html(hud_html, height=920, scrolling=False)
