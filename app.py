import streamlit as st
import json
import os

st.set_page_config(
    page_title="JARVIS",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="collapsed"
)

hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp { background-color: #010816; overflow: hidden; }
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Lógica de gestión de archivo local agenda.json
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
            background-color: #010816;
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
        }
        .core-text {
            position: absolute;
            text-align: center;
            color: #38bdf8;
            z-index: 10;
            pointer-events: none;
        }
        .core-text h1 {
            margin: 0;
            font-size: 32px;
            letter-spacing: 4px;
            color: #22d3ee;
            text-shadow: 0 0 15px rgba(34, 211, 238, 0.9);
        }
        .core-text p {
            margin: 8px 0 0 0;
            font-size: 12px;
            color: #38bdf8;
            letter-spacing: 3px;
        }
        .status-bar {
            position: absolute;
            bottom: 30px;
            color: #0ea5e9;
            font-size: 11px;
            letter-spacing: 2px;
            text-transform: uppercase;
        }
    </style>
</head>
<body>
    <div class="hud-container">
        <canvas id="hudCanvas"></canvas>
        <div class="core-text">
            <h1 id="jarvisTitle">J.A.R.V.I.S.</h1>
            <p id="jarvisStatus">ESCUCHANDO SISTEMA...</p>
        </div>
        <div class="status-bar" id="audioStatus">HAZ CLIC AQUÍ PARA ACTIVAR MICRÓFONO</div>
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

        let particles = [];
        for(let i = 0; i < 50; i++) {
            particles.push({
                angle: Math.random() * Math.PI * 2,
                radius: 130 + Math.random() * 80,
                speed: 0.01 + Math.random() * 0.02,
                size: 1.5 + Math.random() * 2,
                opacity: 0.4 + Math.random() * 0.6
            });
        }

        function drawHUD() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            let cx = canvas.width / 2;
            let cy = canvas.height / 2;

            ctx.strokeStyle = '#0284c7';
            ctx.lineWidth = 1.5;
            ctx.beginPath();
            ctx.arc(cx, cy, 240, 0, Math.PI * 2);
            ctx.stroke();

            ctx.strokeStyle = '#38bdf8';
            ctx.lineWidth = 3;
            ctx.setLineDash([10, 8]);
            ctx.beginPath();
            ctx.arc(cx, cy, 200, 0, Math.PI * 2);
            ctx.stroke();
            ctx.setLineDash([]);

            ctx.strokeStyle = '#0ea5e9';
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.arc(cx, cy, 160, 0, Math.PI * 2);
            ctx.stroke();

            particles.forEach(p => {
                p.angle += p.speed;
                let x = cx + Math.cos(p.angle) * p.radius;
                let y = cy + Math.sin(p.angle) * p.radius;

                ctx.fillStyle = `rgba(56, 189, 248, ${p.opacity})`;
                ctx.beginPath();
                ctx.arc(x, y, p.size, 0, Math.PI * 2);
                ctx.fill();
            });

            ctx.strokeStyle = '#22d3ee';
            ctx.lineWidth = 3;
            ctx.fillStyle = '#010c24';
            ctx.beginPath();
            ctx.arc(cx, cy, 85, 0, Math.PI * 2);
            ctx.fill();
            ctx.stroke();

            requestAnimationFrame(drawHUD);
        }

        drawHUD();

        function hablar(texto) {
            const utterance = new SpeechSynthesisUtterance(texto);
            utterance.lang = 'es-ES';
            utterance.rate = 1.0;
            window.speechSynthesis.speak(utterance);
        }

        // Sistema de tareas guardadas en localStorage del navegador
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

        // Reconocimiento de Voz
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (SpeechRecognition) {
            const recognition = new SpeechRecognition();
            recognition.lang = 'es-ES';
            recognition.continuous = true;
            recognition.interimResults = false;

            recognition.onresult = function(event) {
                const speechResult = event.results[event.results.length - 1][0].transcript.toLowerCase();
                document.getElementById('jarvisStatus').innerText = "COMANDO: " + speechResult.toUpperCase();
                
                // Comandos del Sistema
                if (speechResult.includes("buenos días") || speechResult.includes("hola jarvis")) {
                    hablar("Buenos días, Señor Kion. Sistemas en línea y a su servicio.");
                    setTimeout(() => { document.getElementById('jarvisStatus').innerText = "SISTEMA ACTIVO"; }, 4000);
                } 
                else if (speechResult.includes("descansar") || speechResult.includes("dormir")) {
                    hablar("Entendido. Registrando horario de descanso. Que tenga buenas noches.");
                    setTimeout(() => { document.getElementById('jarvisStatus').innerText = "SISTEMA EN REPOSO"; }, 4000);
                }
                // Comandos de Tareas y Pendientes
                else if (speechResult.includes("agregar tarea") || speechResult.includes("añadir pendiente")) {
                    let nuevaTarea = speechResult.replace("agregar tarea", "").replace("añadir pendiente", "").trim();
                    if (nuevaTarea.length > 0) {
                        guardarTarea(nuevaTarea);
                        hablar("Tarea anotada en su agenda local: " + nuevaTarea);
                    } else {
                        hablar("Por favor especifique la tarea que desea agregar.");
                    }
                }
                else if (speechResult.includes("mis pendientes") || speechResult.includes("mis tareas") || speechResult.includes("lee mis tareas")) {
                    let lista = obtenerTareas();
                    if (lista.length === 0) {
                        hablar("No tiene pendientes registrados en su agenda, Señor Kion.");
                    } else {
                        hablar("Sus pendientes actuales son: " + lista.join(", "));
                    }
                }
                else if (speechResult.includes("limpiar tareas") || speechResult.includes("borrar pendientes")) {
                    limpiarTareas();
                    hablar("Agenda de tareas reiniciada con éxito.");
                }
                // Apertura de Plataformas
                else if (speechResult.includes("youtube")) {
                    hablar("Abriendo YouTube.");
                    setTimeout(() => { window.open("https://www.youtube.com", "_blank"); }, 1000);
                }
                else if (speechResult.includes("notion")) {
                    hablar("Abriendo Notion.");
                    setTimeout(() => { window.open("https://www.notion.so", "_blank"); }, 1000);
                }
                else if (speechResult.includes("calendario")) {
                    hablar("Abriendo Calendario.");
                    setTimeout(() => { window.open("https://calendar.google.com", "_blank"); }, 1000);
                }
                else if (speechResult.includes("canva")) {
                    hablar("Abriendo Canva.");
                    setTimeout(() => { window.open("https://www.canva.com", "_blank"); }, 1000);
                }
                else if (speechResult.includes("whatsapp")) {
                    hablar("Abriendo WhatsApp Web.");
                    setTimeout(() => { window.open("https://web.whatsapp.com", "_blank"); }, 1000);
                }
                else if (speechResult.includes("gemini")) {
                    hablar("Abriendo Gemini.");
                    setTimeout(() => { window.open("https://gemini.google.com", "_blank"); }, 1000);
                }
                else if (speechResult.includes("temporizador")) {
                    hablar("Abriendo temporizador de Google.");
                    setTimeout(() => { window.open("https://www.google.com/search?q=temporizador", "_blank"); }, 1000);
                }
            };

            window.addEventListener('click', () => {
                try {
                    recognition.start();
                    document.getElementById('audioStatus').innerText = "SISTEMA DE VOZ ACTIVO";
                } catch(e) {}
            });
        }

        // Detector de aplausos
        navigator.mediaDevices.getUserMedia({ audio: true, video: false }).then(stream => {
            const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            const analyser = audioCtx.createAnalyser();
            const microphone = audioCtx.createMediaStreamSource(stream);
            microphone.connect(analyser);
            analyser.fftSize = 256;
            const dataArray = new Uint8Array(analyser.frequencyBinCount);
            let bloqueadoPorAplauso = false;

            function detectarSonidoFuerte() {
                if (!bloqueadoPorAplauso) {
                    analyser.getByteFrequencyData(dataArray);
                    let suma = 0;
                    for(let i = 0; i < dataArray.length; i++) {
                        suma += dataArray[i];
                    }
                    let promedio = suma / dataArray.length;

                    if (promedio > 70) {
                        bloqueadoPorAplauso = true;
                        document.getElementById('jarvisStatus').innerText = "APLAUSO DETECTADO";
                        hablar("Sistemas activados por aplauso.");
                        
                        setTimeout(() => {
                            document.getElementById('jarvisStatus').innerText = "SISTEMA ACTIVO";
                            bloqueadoPorAplauso = false;
                        }, 3000);
                    }
                }
                requestAnimationFrame(detectarSonidoFuerte);
            }
            detectarSonidoFuerte();
        }).catch(err => {
            console.log("Micrófono no disponible.");
        });
    </script>
</body>
</html>
"""

import streamlit.components.v1 as components
components.html(hud_html, height=850, scrolling=False)
