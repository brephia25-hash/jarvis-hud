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
    .stApp { background-color: #020b18; overflow: hidden; }
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
        body {
            background-color: #020b18;
            margin: 0;
            overflow: hidden;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            font-family: 'Consolas', monospace;
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
            font-size: 34px;
            letter-spacing: 6px;
            color: #ffffff;
            text-shadow: 0 0 20px #00f3ff, 0 0 40px #00f3ff;
            font-weight: 800;
        }
        .core-text p {
            margin: 10px 0 0 0;
            font-size: 11px;
            color: #38bdf8;
            letter-spacing: 4px;
            text-transform: uppercase;
        }
        .status-bar {
            position: absolute;
            bottom: 25px;
            color: #0ea5e9;
            font-size: 11px;
            letter-spacing: 3px;
            text-transform: uppercase;
            background: rgba(2, 11, 24, 0.8);
            padding: 8px 16px;
            border: 1px solid #00f3ff33;
            border-radius: 4px;
            box-shadow: 0 0 10px rgba(0, 243, 255, 0.2);
            cursor: pointer;
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

        let angleMain = 0;
        let angleInner = 0;
        let angleOuter = 0;

        function drawCircuitLines(cx, cy) {
            ctx.save();
            ctx.strokeStyle = '#0284c7';
            ctx.lineWidth = 1.5;
            ctx.shadowBlur = 8;
            ctx.shadowColor = '#00f3ff';

            // Circuitos Izquierda
            ctx.beginPath();
            ctx.moveTo(0, cy - 100);
            ctx.lineTo(cx - 280, cy - 100);
            ctx.lineTo(cx - 240, cy - 60);
            ctx.lineTo(cx - 200, cy - 60);
            ctx.stroke();

            ctx.beginPath();
            ctx.moveTo(0, cy + 120);
            ctx.lineTo(cx - 320, cy + 120);
            ctx.lineTo(cx - 260, cy + 60);
            ctx.lineTo(cx - 210, cy + 60);
            ctx.stroke();

            // Nodos esquinas circulares
            drawTargetNode(80, cy - 180);
            drawTargetNode(80, cy + 180);

            // Circuitos Derecha
            ctx.beginPath();
            ctx.moveTo(canvas.width, cy - 120);
            ctx.lineTo(cx + 280, cy - 120);
            ctx.lineTo(cx + 230, cy - 70);
            ctx.lineTo(cx + 200, cy - 70);
            ctx.stroke();

            ctx.beginPath();
            ctx.moveTo(canvas.width, cy + 100);
            ctx.lineTo(cx + 310, cy + 100);
            ctx.lineTo(cx + 250, cy + 50);
            ctx.lineTo(cx + 210, cy + 50);
            ctx.stroke();

            drawTargetNode(canvas.width - 80, cy - 180);
            drawTargetNode(canvas.width - 80, cy + 180);

            ctx.restore();
        }

        function drawTargetNode(x, y) {
            ctx.beginPath();
            ctx.arc(x, y, 22, 0, Math.PI * 2);
            ctx.strokeStyle = '#00f3ff';
            ctx.stroke();

            ctx.beginPath();
            ctx.arc(x, y, 14, 0, Math.PI * 2);
            ctx.strokeStyle = '#38bdf8';
            ctx.stroke();

            ctx.beginPath();
            ctx.arc(x, y, 4, 0, Math.PI * 2);
            ctx.fillStyle = '#00f3ff';
            ctx.fill();
        }

        function drawHUD() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            let cx = canvas.width / 2;
            let cy = canvas.height / 2;

            // Dibujar líneas estilo PCB / Circuito de fondo
            drawCircuitLines(cx, cy);

            angleMain += 0.005;
            angleInner -= 0.008;
            angleOuter += 0.003;

            // 1. Anillo Exterior Principal con Cortes
            ctx.save();
            ctx.translate(cx, cy);
            ctx.rotate(angleOuter);
            ctx.strokeStyle = '#00f3ff';
            ctx.lineWidth = 2.5;
            ctx.shadowBlur = 12;
            ctx.shadowColor = '#00f3ff';

            ctx.beginPath();
            ctx.arc(0, 0, 220, 0, Math.PI * 1.4);
            ctx.stroke();

            ctx.beginPath();
            ctx.arc(0, 0, 220, Math.PI * 1.5, Math.PI * 1.9);
            ctx.stroke();
            ctx.restore();

            // 2. Anillo de Escala Graduada (Ticks/Medidores de precisión)
            ctx.save();
            ctx.translate(cx, cy);
            ctx.rotate(angleInner);
            ctx.strokeStyle = '#38bdf8';
            ctx.lineWidth = 1.5;
            for (let i = 0; i < 72; i++) {
                ctx.beginPath();
                let angle = (i * 5) * Math.PI / 180;
                let len = (i % 6 === 0) ? 10 : 5;
                let x1 = Math.cos(angle) * 190;
                let y1 = Math.sin(angle) * 190;
                let x2 = Math.cos(angle) * (190 - len);
                let y2 = Math.sin(angle) * (190 - len);
                ctx.moveTo(x1, y1);
                ctx.lineTo(x2, y2);
                ctx.stroke();
            }
            ctx.restore();

            // 3. Bloques de Barras Radiales (Estilo Ecualizador)
            ctx.save();
            ctx.translate(cx, cy);
            ctx.rotate(angleMain);
            ctx.fillStyle = '#00f3ff';
            for (let i = 0; i < 30; i++) {
                let angle = (i * 4) * Math.PI / 180 + Math.PI;
                let x = Math.cos(angle) * 165;
                let y = Math.sin(angle) * 165;
                ctx.fillRect(x, y, 4, 8);
            }
            ctx.restore();

            // 4. Cadena Digital de Ceros "0000000000"
            ctx.save();
            ctx.translate(cx, cy);
            ctx.rotate(-angleMain * 1.2);
            ctx.fillStyle = '#0ea5e9';
            ctx.font = '10px Consolas';
            let textoCeros = "0000000000000000";
            for (let i = 0; i < textoCeros.length; i++) {
                let angle = (i * 12) * Math.PI / 180 - Math.PI / 2;
                let x = Math.cos(angle) * 145;
                let y = Math.sin(angle) * 145;
                ctx.fillText(textoCeros[i], x, y);
            }
            ctx.restore();

            // 5. Núcleo Interno Sólido
            ctx.save();
            ctx.beginPath();
            ctx.arc(cx, cy, 110, 0, Math.PI * 2);
            ctx.fillStyle = 'rgba(2, 11, 24, 0.95)';
            ctx.fill();
            ctx.strokeStyle = '#00f3ff';
            ctx.lineWidth = 3;
            ctx.shadowBlur = 15;
            ctx.shadowColor = '#00f3ff';
            ctx.stroke();
            ctx.restore();

            requestAnimationFrame(drawHUD);
        }

        drawHUD();

        function hablar(texto) {
            window.speechSynthesis.cancel();
            setTimeout(() => {
                const utterance = new SpeechSynthesisUtterance(texto);
                utterance.lang = 'es-ES';
                utterance.rate = 1.0;
                window.speechSynthesis.speak(utterance);
            }, 100);
        }

        // Gestión de Tareas
        function obtenerTareas() {
            return JSON.parse(localStorage.getItem('jarvis_tareas') || '[]');
        }

        function guardarTarea(tarea) {
            let tareas = obtenerTareas();
            tareas.push(tarea);
            localStorage.setItem('jarvis_tareas', JSON.stringify(tareas));
        }

        function limpiarTareas() {
            localStorage.removeItem('jarvis_tareas');
        }

        // Gestión de Horarios
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

        // Reconocimiento de Voz
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (SpeechRecognition) {
            const recognition = new SpeechRecognition();
            recognition.lang = 'es-ES';
            recognition.continuous = true;
            recognition.interimResults = false;

            recognition.onresult = function(event) {
                const speechResult = event.results[event.results.length - 1][0].transcript.toLowerCase().trim();
                document.getElementById('jarvisStatus').innerText = "COMANDO: " + speechResult.toUpperCase();
                
                // 1. CONSULTAS DE HORARIO
                if (speechResult.includes("desperté") || speechResult.includes("desperte") || speechResult.includes("levanté") || speechResult.includes("levante") || speechResult.includes("hora de inicio")) {
                    let reg = obtenerMomento('despertar');
                    if (!reg) {
                        hablar("No tengo registrado el inicio de su jornada reciente.");
                    } else {
                        hablar("Inició actividad a las " + reg.hora + " del día " + reg.fecha);
                    }
                }
                else if (speechResult.includes("a qué hora me dormí") || speechResult.includes("a que hora me dormi") || speechResult.includes("cuándo descansé") || speechResult.includes("cuando me dormi")) {
                    let reg = obtenerMomento('dormir');
                    if (!reg) {
                        hablar("No tengo registrado un horario de descanso reciente.");
                    } else {
                        hablar("Se registró que se fue a descansar a las " + reg.hora + " del día " + reg.fecha);
                    }
                }

                // 2. ACTIVACIÓN E INICIO
                else if (speechResult.includes("buenos días") || speechResult.includes("buenos dias") || speechResult.includes("buenas noches") || speechResult.includes("hola jarvis")) {
                    let hora = registrarMomento('despertar');
                    hablar("Saludos. Sistemas en línea. Inicio de actividad registrado a las " + hora);
                    setTimeout(() => { document.getElementById('jarvisStatus').innerText = "SISTEMA ACTIVO"; }, 4000);
                } 

                // 3. MODO REPOSO / DESCANSO
                else if (speechResult === "dormir" || speechResult === "descansar" || speechResult.includes("modo descanso") || speechResult.includes("ir a dormir") || speechResult.includes("ir a descansar")) {
                    let hora = registrarMomento('dormir');
                    hablar("Entendido. Hora de descanso registrada a las " + hora + ". Que tenga un buen descanso.");
                    setTimeout(() => { document.getElementById('jarvisStatus').innerText = "SISTEMA EN REPOSO"; }, 4000);
                }

                // 4. COMANDOS DE AGENDA Y TAREAS
                else if (speechResult.includes("agregar tarea") || speechResult.includes("añadir pendiente") || speechResult.includes("agrega la tarea")) {
                    let nuevaTarea = speechResult
                        .replace("agregar tarea", "")
                        .replace("añadir pendiente", "")
                        .replace("agrega la tarea", "")
                        .trim();
                    if (nuevaTarea.length > 0) {
                        guardarTarea(nuevaTarea);
                        document.getElementById('jarvisStatus').innerText = "TAREA AÑADIDA: " + nuevaTarea.toUpperCase();
                        hablar("Tarea anotada en su agenda: " + nuevaTarea);
                    } else {
                        hablar("Por favor especifique la tarea que desea agregar.");
                    }
                }
                else if (speechResult.includes("mis pendientes") || speechResult.includes("mis tareas") || speechResult.includes("lee mis tareas") || speechResult.includes("cuáles son mis tareas") || speechResult.includes("cuales son mis tareas")) {
                    let lista = obtenerTareas();
                    if (lista.length === 0) {
                        document.getElementById('jarvisStatus').innerText = "SIN PENDIENTES";
                        hablar("No tiene pendientes registrados en su agenda.");
                    } else {
                        document.getElementById('jarvisStatus').innerText = "LEYENDO AGENDA...";
                        let textoPendientes = "Sus pendientes actuales son: ";
                        for (let i = 0; i < lista.length; i++) {
                            textoPendientes += "Tarea " + (i + 1) + ": " + lista[i] + ". ";
                        }
                        hablar(textoPendientes);
                    }
                }
                else if (speechResult.includes("limpiar tareas") || speechResult.includes("borrar pendientes") || speechResult.includes("borrar tareas")) {
                    limpiarTareas();
                    document.getElementById('jarvisStatus').innerText = "AGENDA LIMPIA";
                    hablar("Agenda de tareas reiniciada con éxito.");
                }

                // 5. REPRODUCTOR DE MÚSICA POR VOZ
                else if (speechResult.includes("reproduce") || speechResult.includes("reproducir")) {
                    let cancion = speechResult
                        .replace("reproduce", "")
                        .replace("reproducir", "")
                        .trim();
                    if (cancion.length > 0) {
                        hablar("Reproduciendo " + cancion);
                        document.getElementById('jarvisStatus').innerText = "REPRODUCIENDO: " + cancion.toUpperCase();
                        setTimeout(() => { 
                            window.open("https://www.youtube.com/results?search_query=" + encodeURIComponent(cancion), "_blank"); 
                        }, 1000);
                    } else {
                        hablar("Por favor especifique qué canción desea reproducir.");
                    }
                }

                // 6. APERTURA DE PLATAFORMAS
                else if (speechResult.includes("youtube") || speechResult.includes("llutub")) {
                    hablar("Abriendo YouTube.");
                    setTimeout(() => { window.open("https://www.youtube.com", "_blank"); }, 800);
                }
                else if (speechResult.includes("notion") || speechResult.includes("nocion") || speechResult.includes("noishon")) {
                    hablar("Abriendo Notion.");
                    setTimeout(() => { window.open("https://www.notion.so", "_blank"); }, 800);
                }
                else if (speechResult.includes("calendario")) {
                    hablar("Abriendo Calendario.");
                    setTimeout(() => { window.open("https://calendar.google.com", "_blank"); }, 800);
                }
                else if (speechResult.includes("canva")) {
                    hablar("Abriendo Canva.");
                    setTimeout(() => { window.open("https://www.canva.com", "_blank"); }, 800);
                }
                else if (speechResult.includes("whatsapp") || speechResult.includes("wasap")) {
                    hablar("Abriendo WhatsApp Web.");
                    setTimeout(() => { window.open("https://web.whatsapp.com", "_blank"); }, 800);
                }
                else if (speechResult.includes("gemini") || speechResult.includes("gémini") || speechResult.includes("geminis") || speechResult.includes("jemini")) {
                    hablar("Abriendo Gemini.");
                    setTimeout(() => { window.open("https://gemini.google.com", "_blank"); }, 800);
                }
                else if (speechResult.includes("temporizador")) {
                    hablar("Abriendo temporizador de Google.");
                    setTimeout(() => { window.open("https://www.google.com/search?q=temporizador", "_blank"); }, 800);
                }
            };

            window.addEventListener('click', () => {
                try {
                    recognition.start();
                    document.getElementById('audioStatus').innerText = "🎙️ SISTEMA DE VOZ ACTIVO";
                } catch(e) {}
            });
        }
    </script>
</body>
</html>
"""

import streamlit.components.v1 as components
components.html(hud_html, height=850, scrolling=False)
