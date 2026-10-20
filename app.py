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
        }
        .diagnostic-panel {
            position: absolute; top: 20px; right: 25px;
            background: rgba(1, 10, 23, 0.85); border: 1px solid #00f3ff55;
            border-radius: 6px; padding: 10px 16px; color: #00f3ff;
            font-size: 11px; letter-spacing: 2px;
            box-shadow: 0 0 15px rgba(0, 243, 255, 0.2);
            z-index: 20; pointer-events: none; text-align: right;
        }
        .diagnostic-panel .clock {
            font-size: 18px; font-weight: bold; color: #ffffff;
            text-shadow: 0 0 8px #00f3ff; margin-bottom: 2px;
        }
        .diagnostic-panel .sys-info { font-size: 10px; color: #38bdf8; }
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

        let recordatorios = [];
        let alarmas = [];
        let estadoPendienteAMPM = null;
        let alarmaSonandoActiva = false;
        let intervaloAlarmaBucle = null;

        // REVISIÓN CONTINUA DE ALARMAS Y RECORDATORIOS CADA SEGUNDO
        setInterval(() => {
            const now = new Date();
            const horaActualStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false });
            document.getElementById('hudClock').innerText = now.toLocaleTimeString();

            // Evaluar recordatorios
            for (let i = recordatorios.length - 1; i >= 0; i--) {
                if (recordatorios[i].hora === horaActualStr) {
                    let rec = recordatorios.splice(i, 1)[0];
                    if (modoSueno) cambiarTema('normal');
                    hablar("Ey, Señor, recuerde que " + rec.mensaje);
                    document.getElementById('jarvisStatus').innerText = "RECORDATORIO ACTIVO";
                }
            }

            // Evaluar alarmas
            if (!alarmaSonandoActiva) {
                for (let i = alarmas.length - 1; i >= 0; i--) {
                    if (alarmas[i].hora === horaActualStr) {
                        alarmas.splice(i, 1);
                        iniciarBucleAlarma();
                        break;
                    }
                }
            }
        }, 1000);

        function iniciarBucleAlarma() {
            alarmaSonandoActiva = true;
            cambiarTema('normal');
            document.getElementById('jarvisStatus').innerText = "🔔 ALARMA SONANDO";
            
            // Ejecutar ciclo continuo de sonido y mensaje hasta que el usuario diga "silenciar alarma"
            ejecutarRáfagaSonora();
            hablar("Señor, es hora de despertar. Diga silenciar alarma para apagarla.");

            intervaloAlarmaBucle = setInterval(() => {
                if (alarmaSonandoActiva) {
                    ejecutarRáfagaSonora();
                    hablar("Señor, la alarma sigue activa. Diga silenciar alarma.");
                }
            }, 6000);
        }

        function detenciónDefinitivaAlarma() {
            if (alarmaSonandoActiva) {
                alarmaSonandoActiva = false;
                if (intervaloAlarmaBucle) {
                    clearInterval(intervaloAlarmaBucle);
                    intervaloAlarmaBucle = null;
                }
                window.speechSynthesis.cancel();
                document.getElementById('jarvisStatus').innerText = "SISTEMA ACTIVO";
                hablar("Alarma desactivada, Señor.");
            }
        }

        function ejecutarRáfagaSonora() {
            try {
                const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                for(let i = 0; i < 5; i++) {
                    setTimeout(() => {
                        if (!alarmaSonandoActiva) return;
                        const osc = audioCtx.createOscillator();
                        const gain = audioCtx.createGain();
                        osc.type = 'sawtooth';
                        osc.frequency.setValueAtTime(950, audioCtx.currentTime);
                        gain.gain.setValueAtTime(0.2, audioCtx.currentTime);
                        gain.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + 0.35);
                        osc.connect(gain);
                        gain.connect(audioCtx.destination);
                        osc.start();
                        osc.stop(audioCtx.currentTime + 0.35);
                    }, i * 350);
                }
            } catch(e) {}
        }

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
            if (modoSilencio || alarmaSonandoActiva) return;
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
            document.getElementById('audioStatus').style.opacity = "0.3";
            document.getElementById('diagPanel').style.opacity = "0.3";
            theme.primary = '#0284c7'; theme.secondary = '#0369a1';
            theme.darkLine = '#0c4a6e'; theme.dimLine = 'rgba(2, 20, 40, 0.15)';
            document.getElementById('jarvisTitle').style.textShadow = "0 0 10px #0284c7";
            document.getElementById('jarvisStatus').style.color = "#0284c7";
            document.getElementById('jarvisStatus').innerText = "REPOSO PROFUNDO";
            document.getElementById('modeInfo').innerText = "MODO: SUEÑO";
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
            hablar("Enfoque activado: " + minutos + " minutos.");

            timerInterval = setInterval(() => {
                if (tiempoRestanteSegundos <= 0) {
                    clearInterval(timerInterval); timerInterval = null;
                    document.getElementById('jarvisStatus').innerText = "TIEMPO FINALIZADO";
                    hablar("Tiempo finalizado.");
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
                hablar("Sesión cancelada.");
            } else { hablar("No hay enfoque activo."); }
        }

        function obtenerTareas() { return JSON.parse(localStorage.getItem('jarvis_tareas') || '[]'); }
        function guardarTarea(tarea) { let t = obtenerTareas(); t.push(tarea); localStorage.setItem('jarvis_tareas', JSON.stringify(t)); }
        function eliminarTareaUnica(criterio) {
            let t = obtenerTareas();
            if (t.length === 0) return "No hay tareas.";
            let num = parseInt(criterio);
            if (!isNaN(num) && num > 0 && num <= t.length) {
                let borrada = t.splice(num - 1, 1)[0];
                localStorage.setItem('jarvis_tareas', JSON.stringify(t));
                return "Tarea " + num + " eliminada.";
            }
            let idx = t.findIndex(item => item.toLowerCase().includes(criterio.toLowerCase()));
            if (idx !== -1) {
                t.splice(idx, 1);
                localStorage.setItem('jarvis_tareas', JSON.stringify(t));
                return "Tarea eliminada.";
            }
            return "No encontré esa tarea.";
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

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (SpeechRecognition) {
            const recognition = new SpeechRecognition();
            recognition.lang = 'es-ES';
            recognition.continuous = true;
            recognition.interimResults = false;
            let activadoPorUsuario = false;

            recognition.onresult = async function(event) {
                const speechResult = event.results[event.results.length - 1][0].transcript.toLowerCase().trim();

                // 0. DESACTIVACIÓN PRIORITARIA DE ALARMA SONANDO
                if (speechResult.includes("silenciar alarma") || speechResult.includes("apagar alarma") || speechResult.includes("detener alarma") || speechResult.includes("silenciar")) {
                    detenciónDefinitivaAlarma();
                    return;
                }

                // MANEJO DE RESPUESTA PENDIENTE A.M. O P.M.
                if (estadoPendienteAMPM) {
                    emitirPitido();
                    let esPM = speechResult.includes("pm") || speechResult.includes("tarde") || speechResult.includes("noche");
                    let esAM = speechResult.includes("am") || speechResult.includes("mañana");

                    if (esPM || esAM) {
                        let horaFinal = estadoPendienteAMPM.hora;
                        if (esPM && horaFinal < 12) horaFinal += 12;
                        if (esAM && horaFinal === 12) horaFinal = 0;
                        let horaStr = formatearHoraHHMM(horaFinal, estadoPendienteAMPM.min);

                        if (estadoPendienteAMPM.tipo === 'alarma') {
                            alarmas.push({ hora: horaStr });
                            document.getElementById('jarvisStatus').innerText = "ALARMA: " + horaStr;
                            hablar("Alarma programada para las " + horaStr);
                        } else if (estadoPendienteAMPM.tipo === 'recordatorio') {
                            recordatorios.push({ hora: horaStr, mensaje: estadoPendienteAMPM.mensaje });
                            document.getElementById('jarvisStatus').innerText = "RECORDATORIO: " + horaStr;
                            hablar("Recordatorio guardado a las " + horaStr + " para " + estadoPendienteAMPM.mensaje);
                        }
                        estadoPendienteAMPM = null;
                        return;
                    }
                }

                // 1. GESTIÓN DE ALARMAS
                if (speechResult.includes("ver alarmas") || speechResult.includes("mis alarmas") || speechResult.includes("cuáles son mis alarmas")) {
                    emitirPitido();
                    if (alarmas.length === 0) { hablar("No tiene alarmas programadas."); }
                    else {
                        let txt = "Tiene " + alarmas.length + " alarmas: ";
                        for (let i = 0; i < alarmas.length; i++) { txt += "Alarma " + (i + 1) + " a las " + alarmas[i].hora + ". "; }
                        hablar(txt);
                    }
                }
                else if (speechResult.includes("borrar alarma") || speechResult.includes("eliminar alarma") || speechResult.includes("limpiar alarmas")) {
                    emitirPitido();
                    if (speechResult.includes("limpiar") || speechResult.includes("todas")) {
                        alarmas = [];
                        hablar("Todas las alarmas han sido eliminadas.");
                    } else {
                        let num = speechResult.match(/\d+/);
                        let idx = num ? parseInt(num[0]) - 1 : 0;
                        if (idx >= 0 && idx < alarmas.length) {
                            let borrada = alarmas.splice(idx, 1)[0];
                            hablar("Alarma " + (idx + 1) + " eliminada.");
                        } else { hablar("No se encontró esa alarma."); }
                    }
                }
                else if (speechResult.includes("alarma") || speechResult.includes("despiértame") || speechResult.includes("despiertame")) {
                    emitirPitido();
                    let infoHora = analizarHoraTexto(speechResult);
                    if (infoHora) {
                        if (!infoHora.tienePeriodo) {
                            estadoPendienteAMPM = { tipo: 'alarma', hora: infoHora.hora, min: infoHora.min };
                            hablar("¿Desea programar la alarma para la mañana A.M. o para la tarde P.M.?");
                        } else {
                            let hFin = infoHora.hora;
                            if (infoHora.esPM && hFin < 12) hFin += 12;
                            if (!infoHora.esPM && hFin === 12) hFin = 0;
                            let horaStr = formatearHoraHHMM(hFin, infoHora.min);
                            alarmas.push({ hora: horaStr });
                            document.getElementById('jarvisStatus').innerText = "ALARMA: " + horaStr;
                            hablar("Alarma programada a las " + horaStr);
                        }
                    } else { hablar("Por favor especifique la hora de la alarma."); }
                }

                // 2. GESTIÓN DE RECORDATORIOS
                else if (speechResult.includes("ver recordatorios") || speechResult.includes("mis recordatorios") || speechResult.includes("cuáles son mis recordatorios")) {
                    emitirPitido();
                    if (recordatorios.length === 0) { hablar("No tiene recordatorios pendientes."); }
                    else {
                        let txt = "Recordatorios actuales: ";
                        for (let i = 0; i < recordatorios.length; i++) { txt += "Número " + (i + 1) + ": " + recordatorios[i].mensaje + " a las " + recordatorios[i].hora + ". "; }
                        hablar(txt);
                    }
                }
                else if (speechResult.includes("borrar recordatorio") || speechResult.includes("eliminar recordatorio") || speechResult.includes("limpiar recordatorios")) {
                    emitirPitido();
                    if (speechResult.includes("limpiar") || speechResult.includes("todos")) {
                        recordatorios = [];
                        hablar("Todos los recordatorios eliminados.");
                    } else {
                        let num = speechResult.match(/\d+/);
                        let idx = num ? parseInt(num[0]) - 1 : 0;
                        if (idx >= 0 && idx < recordatorios.length) {
                            let borrado = recordatorios.splice(idx, 1)[0];
                            hablar("Recordatorio " + (idx + 1) + " eliminado.");
                        } else { hablar("No encontré ese recordatorio."); }
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
                            hablar("¿El recordatorio es para A.M. o P.M.?");
                        } else {
                            let hFin = infoHora.hora;
                            if (infoHora.esPM && hFin < 12) hFin += 12;
                            if (!infoHora.esPM && hFin === 12) hFin = 0;
                            let horaStr = formatearHoraHHMM(hFin, infoHora.min);
                            recordatorios.push({ hora: horaStr, mensaje: mensajeClean });
                            document.getElementById('jarvisStatus').innerText = "RECORDATORIO: " + horaStr;
                            hablar("Recordatorio guardado a las " + horaStr + " para " + mensajeClean);
                        }
                    } else { hablar("Especifique hora y mensaje para el recordatorio."); }
                }

                // 3. PERSONALIDAD Y DIÁLOGOS
                else if (speechResult.includes("cansado") || speechResult.includes("cansada") || speechResult.includes("agotado")) {
                    emitirPitido();
                    document.getElementById('jarvisStatus').innerText = "ATENCIÓN PERSONAL";
                    hablar("¿Desea que ajuste la iluminación a modo reposo o busque métodos de descanso, Señor?");
                }
                else if (speechResult.includes("aburrido") || speechResult.includes("aburrida")) {
                    emitirPitido();
                    document.getElementById('jarvisStatus').innerText = "SUGERENCIA";
                    hablar("Puedo reproducir algo de música en YouTube o abrir sus plataformas de entretenimiento, Señor.");
                }
                else if (speechResult.includes("mucho trabajo") || speechResult.includes("estresado")) {
                    emitirPitido();
                    document.getElementById('jarvisStatus').innerText = "MODO ASISTENTE";
                    hablar("Le sugiero iniciar una sesión de enfoque con temporizador para organizarlo por partes, Señor.");
                }
                else if (speechResult.includes("cómo estás") || speechResult.includes("como estas") || speechResult.includes("estás ahí")) {
                    emitirPitido();
                    document.getElementById('jarvisStatus').innerText = "ESTADO DEL SISTEMA";
                    hablar("Todos mis sistemas operan al cien por ciento de capacidad y están listos para sus órdenes, Señor.");
                }

                // 4. PLATAFORMAS WEB
                else if (speechResult.includes("gemini") || speechResult.includes("gémini") || speechResult.includes("geminis")) {
                    emitirPitido(); if (modoSueno) cambiarTema('normal');
                    document.getElementById('jarvisStatus').innerText = "ABRIENDO GEMINI";
                    hablar("Abriendo Gemini.");
                    window.open("https://gemini.google.com", "_blank");
                }
                else if (speechResult.includes("pinterest")) {
                    emitirPitido(); if (modoSueno) cambiarTema('normal');
                    document.getElementById('jarvisStatus').innerText = "ABRIENDO PINTEREST";
                    hablar("Abriendo Pinterest.");
                    window.open("https://www.pinterest.com", "_blank");
                }
                else if (speechResult.includes("youtube")) {
                    emitirPitido(); if (modoSueno) cambiarTema('normal');
                    document.getElementById('jarvisStatus').innerText = "ABRIENDO YOUTUBE";
                    hablar("Abriendo YouTube.");
                    window.open("https://www.youtube.com", "_blank");
                }
                else if (speechResult.includes("notion")) {
                    emitirPitido(); if (modoSueno) cambiarTema('normal');
                    document.getElementById('jarvisStatus').innerText = "ABRIENDO NOTION";
                    hablar("Abriendo Notion.");
                    window.open("https://www.notion.so", "_blank");
                }
                else if (speechResult.includes("calendario")) {
                    emitirPitido(); if (modoSueno) cambiarTema('normal');
                    document.getElementById('jarvisStatus').innerText = "ABRIENDO CALENDARIO";
                    hablar("Abriendo Calendario.");
                    window.open("https://calendar.google.com", "_blank");
                }
                else if (speechResult.includes("canva")) {
                    emitirPitido(); if (modoSueno) cambiarTema('normal');
                    document.getElementById('jarvisStatus').innerText = "ABRIENDO CANVA";
                    hablar("Abriendo Canva.");
                    window.open("https://www.canva.com", "_blank");
                }
                else if (speechResult.includes("whatsapp")) {
                    emitirPitido(); if (modoSueno) cambiarTema('normal');
                    document.getElementById('jarvisStatus').innerText = "ABRIENDO WHATSAPP";
                    hablar("Abriendo WhatsApp.");
                    window.open("https://web.whatsapp.com", "_blank");
                }

                // 5. CONTROL GENERAL
                else if (speechResult.includes("modo silencio") || speechResult.includes("silenciar voz")) {
                    emitirPitido(); modoSilencio = true; document.getElementById('jarvisStatus').innerText = "MODO SILENCIO";
                }
                else if (speechResult.includes("desactivar silencio") || speechResult.includes("activar voz")) {
                    emitirPitido(); modoSilencio = false; document.getElementById('jarvisStatus').innerText = "SISTEMA ACTIVO"; hablar("Voz reactivada.");
                }
                else if (speechResult.includes("dormir") || speechResult.includes("descansar") || speechResult.includes("modo descanso")) {
                    emitirPitido(); registrarMomento('dormir'); hablar("Entrando en reposo."); setTimeout(() => { activarModoSueno(); }, 500);
                }
                else if (speechResult.includes("buenos días") || speechResult.includes("buenos dias") || speechResult.includes("hola") || speechResult.includes("despierta")) {
                    emitirPitido(); cambiarTema('normal'); registrarMomento('despertar'); hablar("Sistemas en línea."); setTimeout(() => { document.getElementById('jarvisStatus').innerText = "SISTEMA ACTIVO"; }, 1500);
                }
                else if (speechResult.includes("gracias") || speechResult.includes("agradezco")) {
                    emitirPitido(); if (modoSueno) cambiarTema('normal'); document.getElementById('jarvisStatus').innerText = "A SU SERVICIO"; hablar("A su servicio.");
                }
                else if (speechResult.includes("reformas") || speechResult.includes("mejoras") || speechResult.includes("actualización")) {
                    emitirPitido(); if (modoSueno) cambiarTema('normal'); document.getElementById('jarvisStatus').innerText = "OPTIMIZACIÓN"; hablar("Entendido, Señor.");
                }
                else if (speechResult.includes("qué puedes hacer") || speechResult.includes("que puedes hacer") || speechResult.includes("lista de comandos")) {
                    emitirPitido(); if (modoSueno) cambiarTema('normal'); document.getElementById('jarvisStatus').innerText = "MODO MANUAL";
                    hablar("Sistemas activos. Puedo gestionar alarmas continuas y recordatorios por hora con confirmación A.M. y P.M., registrar tareas y notas, controlar temporizadores, reproducir música, cambiar modos visuales y abrir plataformas web.");
                }
                else if (speechResult.includes("busca") || speechResult.includes("buscar")) {
                    emitirPitido(); if (modoSueno) cambiarTema('normal');
                    let consulta = speechResult.replace("busca en google", "").replace("buscar en google", "").replace("busca", "").replace("buscar", "").trim();
                    if (consulta.length > 0) { hablar("Buscando..."); document.getElementById('jarvisStatus').innerText = "BUSCANDO..."; window.open("https://www.google.com/search?q=" + encodeURIComponent(consulta), "_blank"); }
                    else { hablar("Especifique qué buscar."); }
                }
                else if (speechResult.includes("modo sigiloso") || speechResult.includes("protocolo nocturno")) {
                    emitirPitido(); cambiarTema('sigilo'); document.getElementById('jarvisStatus').innerText = "MODO SIGILO"; hablar("Modo sigilo.");
                }
                else if (speechResult.includes("modo normal") || speechResult.includes("protocolo estándar")) {
                    emitirPitido(); cambiarTema('normal'); document.getElementById('jarvisStatus').innerText = "MODO ESTÁNDAR"; hablar("Modo estándar.");
                }
                else if (speechResult.includes("detener enfoque") || speechResult.includes("cancelar enfoque")) {
                    emitirPitido(); if (modoSueno) cambiarTema('normal'); detenerTemporizadorEnfoque();
                }
                else if (speechResult.includes("iniciar sesión de estudio") || speechResult.includes("modo enfoque")) {
                    emitirPitido(); if (modoSueno) cambiarTema('normal');
                    let num = speechResult.match(/\d+/);
                    iniciarTemporizadorEnfoque(num ? parseInt(num[0]) : 25);
                }
                else if (speechResult.includes("anota nota") || speechResult.includes("guarda la nota")) {
                    emitirPitido(); if (modoSueno) cambiarTema('normal');
                    let txt = speechResult.replace("anota nota", "").replace("guarda la nota", "").trim();
                    if (txt.length > 0) { guardarNota(txt); hablar("Nota registrada."); } else { hablar("Especifique la nota."); }
                }
                else if (speechResult.includes("mis notas")) {
                    emitirPitido(); if (modoSueno) cambiarTema('normal');
                    let n = obtenerNotas(); hablar(n.length === 0 ? "Sin notas." : "Notas: " + n.join(". "));
                }
                else if (speechResult.includes("limpiar notas")) {
                    emitirPitido(); if (modoSueno) cambiarTema('normal'); limpiarNotas(); hablar("Notas borradas.");
                }
                else if (speechResult.includes("eliminar tarea") || speechResult.includes("borrar tarea")) {
                    emitirPitido(); if (modoSueno) cambiarTema('normal');
                    let crit = speechResult.replace("eliminar tarea", "").replace("borrar tarea", "").trim();
                    hablar(eliminarTareaUnica(crit));
                }
                else if (speechResult.includes("agregar tarea") || speechResult.includes("añadir pendiente")) {
                    emitirPitido(); if (modoSueno) cambiarTema('normal');
                    let nT = speechResult.replace("agregar tarea", "").replace("añadir pendiente", "").trim();
                    if (nT.length > 0) { guardarTarea(nT); hablar("Tarea anotada."); } else { hablar("Especifique la tarea."); }
                }
                else if (speechResult.includes("mis pendientes") || speechResult.includes("mis tareas")) {
                    emitirPitido(); if (modoSueno) cambiarTema('normal');
                    let l = obtenerTareas();
                    if (l.length === 0) { hablar("No tiene pendientes."); }
                    else { let txt = "Pendientes: "; for (let i = 0; i < l.length; i++) { txt += (i + 1) + ", " + l[i] + ". "; } hablar(txt); }
                }
                else if (speechResult.includes("limpiar tareas")) {
                    emitirPitido(); if (modoSueno) cambiarTema('normal'); limpiarTareas(); hablar("Agenda limpia.");
                }
                else if (speechResult.includes("reproduce") || speechResult.includes("reproducir")) {
                    emitirPitido(); if (modoSueno) cambiarTema('normal');
                    let cancion = speechResult.replace("reproduce", "").replace("reproducir", "").trim();
                    if (cancion.length > 0) { hablar("Reproduciendo."); window.open("https://www.youtube.com/results?search_query=" + encodeURIComponent(cancion), "_blank"); }
                    else { hablar("Especifique la canción."); }
                }
            };

            recognition.onend = function() {
                if (activadoPorUsuario) { try { recognition.start(); } catch(e) {} }
            };

            recognition.onerror = function(event) {
                if (activadoPorUsuario) { setTimeout(() => { try { recognition.start(); } catch(e) {} }, 300); }
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
