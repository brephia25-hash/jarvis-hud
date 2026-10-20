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
    .stApp { background-color: #010a17; overflow: hidden; }
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
            background-color: #010a17;
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
            font-size: 36px;
            letter-spacing: 7px;
            color: #ffffff;
            text-shadow: 0 0 20px #00f3ff, 0 0 40px #00f3ff;
            font-weight: 800;
        }
        .core-text p {
            margin: 8px 0 0 0;
            font-size: 11px;
            color: #38bdf8;
            letter-spacing: 4px;
            text-transform: uppercase;
        }
        .status-bar {
            position: absolute;
            bottom: 20px;
            color: #0ea5e9;
            font-size: 11px;
            letter-spacing: 3px;
            text-transform: uppercase;
            background: rgba(1, 10, 23, 0.85);
            padding: 8px 18px;
            border: 1px solid #00f3ff44;
            border-radius: 4px;
            box-shadow: 0 0 12px rgba(0, 243, 255, 0.25);
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

        let theme = {
            primary: '#00f3ff',
            secondary: '#38bdf8',
            darkLine: '#0284c7',
            dimLine: 'rgba(2, 40, 80, 0.35)',
            glow: 'rgba(0, 243, 255, 0.9)'
        };

        function cambiarTema(modo) {
            if (modo === 'sigilo') {
                theme.primary = '#ff2a2a';
                theme.secondary = '#f87171';
                theme.darkLine = '#991b1b';
                theme.dimLine = 'rgba(80, 10, 10, 0.35)';
                theme.glow = 'rgba(255, 42, 42, 0.9)';
                document.getElementById('jarvisTitle').style.textShadow = "0 0 20px #ff2a2a, 0 0 40px #ff2a2a";
                document.getElementById('jarvisStatus').style.color = "#f87171";
            } else {
                theme.primary = '#00f3ff';
                theme.secondary = '#38bdf8';
                theme.darkLine = '#0284c7';
                theme.dimLine = 'rgba(2, 40, 80, 0.35)';
                theme.glow = 'rgba(0, 243, 255, 0.9)';
                document.getElementById('jarvisTitle').style.textShadow = "0 0 20px #00f3ff, 0 0 40px #00f3ff";
                document.getElementById('jarvisStatus').style.color = "#38bdf8";
            }
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
            ctx.shadowBlur = 10;
            ctx.shadowColor = theme.primary;
            ctx.fill();
        }

        function drawTargetNode(x, y, size = 26) {
            ctx.save();
            ctx.strokeStyle = theme.primary;
            ctx.lineWidth = 1.8;
            ctx.shadowBlur = 10;
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
            ctx.shadowBlur = 8;
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

            angleMain += 0.004;
            angleInner -= 0.006;
            angleOuter += 0.002;

            ctx.save();
            ctx.translate(cx, cy);
            ctx.rotate(angleOuter);
            ctx.strokeStyle = theme.primary;
            ctx.lineWidth = 3;
            ctx.shadowBlur = 15;
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

            ctx.save();
            ctx.beginPath();
            ctx.arc(cx, cy, 118, 0, Math.PI * 2);
            ctx.fillStyle = 'rgba(1, 10, 23, 0.95)';
            ctx.fill();
            ctx.strokeStyle = theme.primary;
            ctx.lineWidth = 3.5;
            ctx.shadowBlur = 20;
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
            if (timerInterval) {
                clearInterval(timerInterval);
                timerInterval = null;
            }
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
                document.getElementById('jarvisStatus').innerText = "SISTEMA ACTIVO";
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

                // 7. CANCELAR O DETENER TEMPORIZADOR DE ENFOQUE (MEJORADO)
                else if (speechResult.includes("detener enfoque") || speechResult.includes("detén el enfoque") || speechResult.includes("deten el enfoque") || speechResult.includes("para el enfoque") || speechResult.includes("cancelar enfoque") || speechResult.includes("cancelar temporizador") || speechResult.includes("detener temporizador")) {
                    detenerTemporizadorEnfoque();
                }

                // 8. INICIAR TEMPORIZADOR DE ENFOQUE (POMODORO)
                else if (speechResult.includes("iniciar sesión de estudio") || speechResult.includes("iniciar sesion de estudio") || speechResult.includes("modo enfoque") || speechResult.includes("temporizador de")) {
                    let numeros = speechResult.match(/\d+/);
                    let minutos = numeros ? parseInt(numeros[0]) : 25;
                    iniciarTemporizadorEnfoque(minutos);
                }

                // 9. BLOC DE NOTAS RÁPIDO POR VOZ
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

                // 10. INFORME METEOROLÓGICO
                else if (speechResult.includes("clima") || speechResult.includes("reporte meteorológico") || speechResult.includes("temperatura")) {
                    document.getElementById('jarvisStatus').innerText = "CONSULTANDO CLIMA...";
                    let reporte = await obtenerClima();
                    document.getElementById('jarvisStatus').innerText = "SISTEMA ACTIVO";
                    hablar(reporte);
                }

                // 11. ELIMINAR UNA SOLA TAREA
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

                // 12. COMANDOS GENERALES DE AGENDA
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

                // 13. REPRODUCTOR DE MÚSICA POR VOZ
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

                // 14. APERTURA DE PLATAFORMAS
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
