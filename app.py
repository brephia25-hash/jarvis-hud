import datetime
import os
import sqlite3
import streamlit as st
from gtts import gTTS

st.set_page_config(
    page_title="JARVIS - HUD",
    page_icon="💻",
    layout="wide"
)

USER_NAME = "Señor Kion"

def iniciar_db():
    conn = sqlite3.connect("jarvis_memory.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS registro_sueno (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            tipo TEXT,
            hora TEXT
        )
    """)
    conn.commit()
    conn.close()

iniciar_db()

def hablar(texto):
    try:
        tts = gTTS(text=texto, lang="es", slow=False)
        tts.save("respuesta.mp3")
    except Exception:
        pass

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
            width: 600px;
            height: 600px;
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
            color: #38bdf8;
            z-index: 10;
            pointer-events: none;
        }
        .core-text h1 {
            margin: 0;
            font-size: 24px;
            letter-spacing: 3px;
            color: #22d3ee;
            text-shadow: 0 0 10px rgba(34, 211, 238, 0.8);
        }
        .core-text p {
            margin: 5px 0 0 0;
            font-size: 10px;
            color: #38bdf8;
            letter-spacing: 2px;
        }
    </style>
</head>
<body>
    <div class="hud-container">
        <canvas id="hudCanvas" width="600" height="600"></canvas>
        <div class="core-text">
            <h1>J.A.R.V.I.S.</h1>
            <p>SISTEMA ACTIVO</p>
        </div>
    </div>

    <script>
        const canvas = document.getElementById('hudCanvas');
        const ctx = canvas.getContext('2d');
        
        const cx = 300;
        const cy = 300;

        let particles = [];
        for(let i = 0; i < 35; i++) {
            particles.push({
                angle: Math.random() * Math.PI * 2,
                radius: 110 + Math.random() * 60,
                speed: 0.015 + Math.random() * 0.02,
                size: 1.5 + Math.random() * 2,
                opacity: 0.5 + Math.random() * 0.5
            });
        }

        function drawHUD() {
            ctx.clearRect(0, 0, 600, 600);

            ctx.strokeStyle = '#0284c7';
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(20, 150); ctx.lineTo(120, 150); ctx.lineTo(160, 190);
            ctx.moveTo(580, 150); ctx.lineTo(480, 150); ctx.lineTo(440, 190);
            ctx.moveTo(40, 450); ctx.lineTo(140, 450); ctx.lineTo(180, 410);
            ctx.moveTo(560, 450); ctx.lineTo(460, 450); ctx.lineTo(420, 410);
            ctx.stroke();

            ctx.fillStyle = '#38bdf8';
            ctx.fillRect(18, 147, 6, 6);
            ctx.fillRect(576, 147, 6, 6);

            ctx.strokeStyle = '#0284c7';
            ctx.lineWidth = 1.5;
            ctx.beginPath();
            ctx.arc(cx, cy, 220, 0, Math.PI * 2);
            ctx.stroke();

            ctx.strokeStyle = '#38bdf8';
            ctx.lineWidth = 3;
            ctx.setLineDash([8, 6]);
            ctx.beginPath();
            ctx.arc(cx, cy, 180, 0, Math.PI * 2);
            ctx.stroke();
            ctx.setLineDash([]);

            ctx.strokeStyle = '#0ea5e9';
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.arc(cx, cy, 140, 0, Math.PI * 2);
            ctx.stroke();

            ctx.font = '9px Consolas';
            ctx.fillStyle = '#38bdf8';
            ctx.fillText("0000000000000000", 215, 115);
            ctx.fillText("0000000000000000", 215, 495);

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
            ctx.arc(cx, cy, 70, 0, Math.PI * 2);
            ctx.fill();
            ctx.stroke();

            requestAnimationFrame(drawHUD);
        }

        drawHUD();
    </script>
</body>
</html>
"""

import streamlit.components.v1 as components
components.html(hud_html, height=620)

st.markdown("<h3 style='text-align: center; color: #22d3ee;'>PANEL DE COMANDOS</h3>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Registrar Despertar", use_container_width=True):
        ahora = datetime.datetime.now()
        conn = sqlite3.connect("jarvis_memory.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO registro_sueno (fecha, tipo, hora) VALUES (?, ?, ?)", (ahora.strftime("%Y-%m-%d"), "despertar", ahora.strftime("%H:%M:%S")))
        conn.commit()
        conn.close()
        st.success(f"Despertar registrado a las {ahora.strftime('%H:%M:%S')}.")
        hablar("Despertar registrado con exito.")

with col2:
    if st.button("Registrar Dormir", use_container_width=True):
        ahora = datetime.datetime.now()
        conn = sqlite3.connect("jarvis_memory.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO registro_sueno (fecha, tipo, hora) VALUES (?, ?, ?)", (ahora.strftime("%Y-%m-%d"), "dormir", ahora.strftime("%H:%M:%S")))
        conn.commit()
        conn.close()
        st.info("Horario de descanso guardado.")
        hablar("Buenas noches.")

with col3:
    if st.button("Simular Activacion por Voz/Aplauso", use_container_width=True):
        st.balloons()
        st.success("JARVIS activado correctamente.")
        hablar("Sistemas en linea. A su servicio.")

st.markdown("<h4 style='color: #0ea5e9;'>ACCESOS DIRECTOS</h4>", unsafe_allow_html=True)
b1, b2, b3, b4 = st.columns(4)

with b1:
    if st.button("YouTube"):
        st.markdown('<meta http-equiv="refresh" content="0;url=https://www.youtube.com">', unsafe_allow_html=True)
with b2:
    if st.button("Notion"):
        st.markdown('<meta http-equiv="refresh" content="0;url=https://www.notion.so">', unsafe_allow_html=True)
with b3:
    if st.button("WhatsApp"):
        st.markdown('<meta http-equiv="refresh" content="0;url=https://web.whatsapp.com">', unsafe_allow_html=True)
with b4:
    if st.button("Gemini"):
        st.markdown('<meta http-equiv="refresh" content="0;url=https://gemini.google.com">', unsafe_allow_html=True)
