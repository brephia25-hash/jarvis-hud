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
            transition: background-color 0.5s ease;
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
            transition: color 0.5s ease, text-shadow 0.5s ease;
        }
        .core-text p {
            margin: 10px 0 0 0;
            font-size: 11px;
            color: #38bdf8;
            letter-spacing: 4px;
            text-transform: uppercase;
            transition: color 0.5s ease;
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
            transition: border-color 0.5s ease, color 0.5s ease;
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

        let theme = {
            primary: '#00f3ff',
            secondary: '#38bdf8',
            darkLine: '#0284c7',
            coreGlow: 'rgba(0, 243, 255, 0.9)'
        };

        function cambiarTema(modo) {
            if (modo === 'sigilo') {
                theme.primary = '#ff2a2a';
                theme.secondary = '#f87171';
                theme.darkLine = '#991b1b';
                theme.coreGlow = 'rgba(255, 42, 42, 0.9)';
                document.getElementById('jarvisTitle').style.textShadow = "0 0 20px #ff2a2a, 0 0 40px #ff2a2a";
                document.getElementById('jarvisTitle').style.color = "#ffffff";
                document.getElementById('jarvisStatus').style.color = "#f87171";
            } else {
                theme.primary = '#00f3ff';
                theme.secondary = '#38bdf8';
                theme.darkLine = '#0284c7';
                theme.coreGlow = 'rgba(0, 243, 255, 0.9)';
                document.getElementById('jarvisTitle').style.textShadow = "0 0 20px #00f3ff, 0 0 40px #00f3ff";
                document.getElementById('jarvisTitle').style.color = "#ffffff";
                document.getElementById('jarvisStatus').style.color = "#38bdf8";
            }
        }

        let timerInterval = null;
        let tiempoRestanteSegundos = 0;

        function drawCircuitLines(cx, cy) {
            ctx.save();
            ctx.strokeStyle = theme.darkLine;
            ctx.lineWidth = 1.5;
            ctx.shadowBlur = 8;
            ctx.shadowColor = theme.primary;

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

            drawTargetNode(80, cy - 180);
            drawTargetNode(80, cy + 180);

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
            ctx.strokeStyle = theme.primary;
            ctx.stroke();

            ctx.beginPath();
            ctx.arc(x, y, 14, 0, Math.PI * 2);
            ctx.strokeStyle = theme.secondary;
            ctx.stroke();

            ctx.beginPath();
            ctx.arc(x, y, 4, 0, Math.PI * 2);
            ctx.fillStyle = theme.primary;
            ctx.fill();
        }

        function drawHUD() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            let cx = canvas.width / 2;
            let cy = canvas.height / 2;

            drawCircuitLines(cx, cy);

            angleMain += 0.005;
            angleInner -= 0.008;
            angleOuter += 0.003;

            ctx.save();
            ctx.translate(cx, cy);
            ctx.rotate(angleOuter);
            ctx.strokeStyle = theme.primary;
            ctx.lineWidth = 2.5;
            ctx.shadowBlur = 12;
            ctx.shadowColor = theme.primary;

            ctx.beginPath();
            ctx.arc(0, 0, 220, 0, Math.PI * 1.4);
            ctx.stroke();

            ctx.beginPath();
            ctx.arc(0, 0, 220, Math.PI * 1.5, Math.PI * 1.9);
            ctx.stroke();
            ctx.restore();

            ctx.save();
            ctx.translate(cx, cy);
            ctx.rotate(angleInner);
            ctx.strokeStyle = theme.secondary;
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

            ctx.save();
            ctx.translate(cx, cy);
            ctx.rotate(angleMain);
            ctx.fillStyle = theme.primary;
            for (let i = 0; i < 30; i++) {
                let angle = (i * 4) * Math.PI / 180 + Math.PI;
                let x = Math.cos(angle) * 165;
                let y = Math.sin(angle) * 165;
                ctx.fillRect(x, y, 4, 8);
            }
            ctx.restore();

            ctx.save();
            ctx.translate(cx, cy);
            ctx.rotate(-angleMain * 1.2);
            ctx.fillStyle = theme.secondary;
            ctx.font = '10px Consolas';
            let textoCeros = "0000000000000000";
            for (let i = 0; i < textoCeros.length; i++) {
                let angle = (i * 12) * Math.PI / 180 - Math.PI / 2;
                let x = Math.cos(angle) * 145;
                let y = Math.sin(angle) * 145;
                ctx.fillText(textoCeros[i], x, y);
            }
            ctx.restore();

            ctx.save();
            ctx.beginPath();
            ctx.arc(cx, cy, 110, 0, Math.PI * 2);
            ctx.fillStyle = 'rgba(2, 11, 24, 0.95)';
            ctx.fill();
            ctx.strokeStyle = theme.primary;
            ctx.lineWidth = 3;
            ctx.shadowBlur = 15;
            ctx.shadowColor = theme.primary;
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

        function iniciarTemporizadorEnfoque(minutos) {
            if (timerInterval) clearInterval(timerInterval);
            tiempoRestanteSegundos = minutos * 60;

            hablar("Iniciando sesión de enfoque por " + minutos + " minutos. Concentración activada.");

            timerInterval = setInterval(() => {
                if (tiempoRestanteSegundos <= 0) {
                    clearInterval(timerInterval);
                    timerInterval = null;
                    document.getElementById('jarvisStatus').innerText = "TIEMPO FINALIZADO";
                    hablar("Tiempo de enfoque finalizado. Es momento de tomar un descanso.");
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
                document.getElementById('jarvisStatus').innerText = "TEMPORIZADOR DETENIDO";
                hablar("Sesión de enfoque cancelada.");
            } else {
                hablar("No hay ninguna sesión de enfoque activa.");
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
                return { exito: true, mensaje: "Tarea " + numero + " eliminada: " + borrada };
            }

            let indiceEncontrado = tareas.findIndex(t => t.toLowerCase().includes(criterio.toLowerCase()));
            if (indiceEncontrado !== -1) {
                let borrada = tareas.splice(indiceEncontrado, 1)[0];
                localStorage.setItem('jarvis_tareas', JSON.stringify(tareas));
                return { exito: true, mensaje: "Tarea eliminada: " + borrada };
            }

            return { exito: false, mensaje: "No encontré ninguna tarea con ese número o nombre." };
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

        async function obtenerClima() {
            try {
                const res = await fetch('https://api.open-meteo.com/v1/forecast?latitude=10.48801&longitude=-66.87919&current_weather=true');
                const data = await res.json();
                if (data && data.current_weather) {
                    let temp = Math.round(data.current_weather.temperature);
                    return "La temperatura actual en Caracas es de " + temp + " grados centígrados.";
                }
            } catch(e) {}
            return "No pude obtener la información del clima en este momento.";
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

            recognition.onresult = async function(event) {
                const speechResult = event.results[event.results.length - 1][0].transcript.toLowerCase().trim();
                
                // 1. REFORMAS Y MEJORAS
                if (speechResult.includes("reformas") || speechResult.includes("mejoras") || speechResult.includes("actualización") || speechResult.includes("actualizacion")) {
                    document.getElementById('jarvisStatus').innerText = "MODO OPTIMIZACIÓN";
                    hablar("Entendido, Señor. Estaré esperando mis próximas mejoras para optimizar mis sistemas.");
                }

                // 2. LISTA DE COMANDOS Y FUNCIONES
                else if (speechResult.includes("qué puedes hacer") || speechResult.includes("que puedes hacer") || speechResult.includes("cuáles son tus funciones") || speechResult.includes("cuales son tus funciones") || speechResult.includes("lista de comandos") || speechResult.includes("manual de funciones")) {
                    document.getElementById('jarvisStatus').innerText = "MOSTRANDO FUNCIONES";
                    hablar("Mis capacidades principales incluyen: registrar su horario de descanso y despertar, gestionar sus tareas y notas rápidas, iniciar sesiones de enfoque con temporizador, informar el clima local, reproducir música en YouTube, cambiar a modo sigilo y abrir sus plataformas habituales.");
                }

                // 3. CONSULTAS DE HORARIO
                else if (speechResult.includes("desperté") || speechResult.includes("desperte") || speechResult.includes("levanté") || speechResult.includes("levante") || speechResult.includes("hora de inicio")) {
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

                // 4. ACTIVACIÓN E INICIO
                else if (speechResult.includes("buenos días") || speechResult.includes("buenos dias") || speechResult.includes("buenas noches") || speechResult.includes("hola jarvis")) {
                    let hora = registrarMomento('despertar');
                    hablar("Saludos. Sistemas en línea. Inicio de actividad registrado a las " + hora);
                    setTimeout(() => { document.getElementById('jarvisStatus').innerText = "SISTEMA ACTIVO"; }, 4000);
                } 

                // 5. MODO REPOSO / DESCANSO
                else if (speechResult === "dormir" || speechResult === "descansar" || speechResult.includes("modo descanso") || speechResult.includes("ir a dormir") || speechResult.includes("ir a descansar")) {
                    let hora = registrarMomento('dormir');
                    hablar("Entendido. Hora de descanso registrada a las " + hora + ". Que tenga un buen descanso.");
                    setTimeout(() => { document.getElementById('jarvisStatus').innerText = "SISTEMA EN REPOSO"; }, 4000);
                }

                // 6. CONTROL DE MODO VISUAL HUD
                else if (speechResult.includes("modo sigiloso") || speechResult.includes("protocolo nocturno") || speechResult.includes("modo rojo")) {
                    cambiarTema('sigilo');
                    document.getElementById('jarvisStatus').innerText = "MODO SIGILO ACTIVO";
                    hablar("Protocolo nocturno activado. Ajustando espectro visual.");
                }
                else if (speechResult.includes("modo normal") || speechResult.includes("protocolo estándar") || speechResult.includes("modo cian")) {
                    cambiarTema('normal');
                    document.getElementById('jarvisStatus').innerText = "MODO ESTÁNDAR";
                    hablar("Sistemas restaurados a interfaz estándar.");
                }

                // 7. TEMPORIZADOR DE ENFOQUE (POMODORO)
                else if (speechResult.includes("iniciar sesión de estudio") || speechResult.includes("iniciar sesion de estudio") || speechResult.includes("modo enfoque") || speechResult.includes("temporizador de")) {
                    let numeros = speechResult.match(/\d+/);
                    let minutos = numeros ? parseInt(numeros[0]) : 25;
                    iniciarTemporizadorEnfoque(minutos);
                }
                else if (speechResult.includes("cancelar temporizador") || speechResult.includes("detener enfoque") || speechResult.includes("cancelar enfoque")) {
                    detenerTemporizadorEnfoque();
                }

                // 8. BLOC DE NOTAS RÁPIDO POR VOZ
                else if (speechResult.includes("anota nota") || speechResult.includes("guarda la nota") || speechResult.includes("nueva nota")) {
                    let notaText = speechResult
                        .replace("anota nota", "")
                        .replace("guarda la nota", "")
                        .replace("nueva nota", "")
                        .trim();
                    if (notaText.length > 0) {
                        guardarNota(notaText);
                        document.getElementById('jarvisStatus').innerText = "NOTA GUARDADA";
                        hablar("Nota registrada: " + notaText);
                    } else {
                        hablar("Por favor especifique el contenido de la nota.");
                    }
                }
                else if (speechResult.includes("mis notas") || speechResult.includes("lee mis notas") || speechResult.includes("cuáles son mis notas")) {
                    let notas = obtenerNotas();
                    if (notas.length === 0) {
                        hablar("No tiene notas registradas.");
                    } else {
                        hablar("Sus notas son: " + notas.join(". "));
                    }
                }
                else if (speechResult.includes("limpiar notas") || speechResult.includes("borrar notas")) {
                    limpiarNotas();
                    hablar("Notas eliminadas con éxito.");
                }

                // 9. INFORME METEOROLÓGICO
                else if (speechResult.includes("clima") || speechResult.includes("reporte meteorológico") || speechResult.includes("temperatura")) {
                    document.getElementById('jarvisStatus').innerText = "CONSULTANDO CLIMA...";
                    let reporte = await obtenerClima();
                    document.getElementById('jarvisStatus').innerText = "SISTEMA ACTIVO";
                    hablar(reporte);
                }

                // 10. ELIMINAR UNA SOLA TAREA
                else if (speechResult.includes("eliminar tarea") || speechResult.includes("borrar tarea") || speechResult.includes("quitar tarea")) {
                    let criterio = speechResult
                        .replace("eliminar tarea", "")
                        .replace("borrar tarea", "")
                        .replace("quitar tarea", "")
                        .replace("número", "")
                        .replace("numero", "")
                        .trim();
                    if (criterio.length > 0) {
                        let res = eliminarTareaUnica(criterio);
                        document.getElementById('jarvisStatus').innerText = res.exito ? "TAREA ELIMINADA" : "ERROR";
                        hablar(res.mensaje);
                    } else {
                        hablar("Por favor especifique el número o nombre de la tarea que desea eliminar.");
                    }
                }

                // 11. COMANDOS GENERALES DE AGENDA
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
                else if (speechResult.includes("limpiar tareas") || speechResult.includes("borrar pendientes") || speechResult.includes("borrar todas las tareas")) {
                    limpiarTareas();
                    document.getElementById('jarvisStatus').innerText = "AGENDA LIMPIA";
                    hablar("Agenda de tareas reiniciada con éxito.");
                }

                // 12. REPRODUCTOR DE MÚSICA POR VOZ
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

                // 13. APERTURA DE PLATAFORMAS
                else if (speechResult.includes("pinterest") || speechResult.includes("pinteres")) {
                    hablar("Abriendo Pinterest.");
                    setTimeout(() => { window.open("https://www.pinterest.com", "_blank"); }, 800);
                }
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
