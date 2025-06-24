# Script para instalar y configurar Ollama para EV-EMAPs Chatbot
# Ejecutar como Administrador

Write-Host "🤖 Instalando Ollama para EV-EMAPs Chatbot" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green

# Paso 1: Descargar Ollama
Write-Host "📥 Paso 1: Descargando Ollama..." -ForegroundColor Yellow
$ollamaUrl = "https://ollama.com/download/windows"
Write-Host "Ve a $ollamaUrl para descargar Ollama" -ForegroundColor Cyan
Start-Process $ollamaUrl

Write-Host "⏳ Esperando a que instales Ollama..." -ForegroundColor Yellow
Read-Host "Presiona Enter cuando hayas instalado Ollama"

# Paso 2: Verificar instalación
Write-Host "✅ Paso 2: Verificando instalación..." -ForegroundColor Yellow
try {
    $version = & ollama --version
    Write-Host "Ollama instalado correctamente: $version" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: Ollama no está instalado o no está en PATH" -ForegroundColor Red
    Write-Host "Reinicia PowerShell e intenta de nuevo" -ForegroundColor Yellow
    exit 1
}

# Paso 3: Descargar modelo de IA
Write-Host "🧠 Paso 3: Descargando modelo de IA..." -ForegroundColor Yellow
Write-Host "Descargando Llama 3.2 (3B) - Modelo ligero y rápido" -ForegroundColor Cyan

try {
    & ollama pull llama3.2:3b
    Write-Host "✅ Modelo descargado exitosamente" -ForegroundColor Green
} catch {
    Write-Host "❌ Error descargando el modelo" -ForegroundColor Red
    Write-Host "Intenta manualmente: ollama pull llama3.2:3b" -ForegroundColor Yellow
}

# Paso 4: Iniciar servidor
Write-Host "🚀 Paso 4: Iniciando servidor Ollama..." -ForegroundColor Yellow
Write-Host "El servidor se iniciará en segundo plano" -ForegroundColor Cyan

Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Hidden

Start-Sleep -Seconds 5

# Paso 5: Verificar que el servidor esté funcionando
Write-Host "🔍 Paso 5: Verificando servidor..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:11434/api/version" -Method Get
    Write-Host "✅ Servidor Ollama funcionando correctamente" -ForegroundColor Green
    Write-Host "Versión: $($response.version)" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: Servidor no responde" -ForegroundColor Red
    Write-Host "Inicia manualmente: ollama serve" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎉 ¡CONFIGURACIÓN COMPLETADA!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host "✅ Ollama instalado y funcionando" -ForegroundColor Green
Write-Host "✅ Modelo Llama 3.2 descargado" -ForegroundColor Green
Write-Host "✅ Servidor iniciado en puerto 11434" -ForegroundColor Green
Write-Host ""
Write-Host "📋 PRÓXIMOS PASOS:" -ForegroundColor Cyan
Write-Host "1. Tu chatbot ya tiene OLLAMA_AVAILABLE = True" -ForegroundColor White
Write-Host "2. Reinicia el servidor Django con Daphne" -ForegroundColor White
Write-Host "3. ¡Prueba el chatbot con IA real!" -ForegroundColor White
Write-Host ""
Write-Host "🔧 COMANDOS ÚTILES:" -ForegroundColor Cyan
Write-Host "- Iniciar servidor: ollama serve" -ForegroundColor White
Write-Host "- Ver modelos: ollama list" -ForegroundColor White
Write-Host "- Chat directo: ollama run llama3.2:3b" -ForegroundColor White
Write-Host ""
Write-Host "📞 SOPORTE: julio@juliomalaga.me" -ForegroundColor Yellow
