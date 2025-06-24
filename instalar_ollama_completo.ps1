# Script mejorado para instalar Ollama correctamente
# Ejecutar como Administrador

Write-Host "🤖 Instalando Ollama para EV-EMAPs Chatbot (Método Completo)" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green

# Paso 1: Descargar e instalar Ollama
Write-Host "📥 Paso 1: Descargando e instalando Ollama..." -ForegroundColor Yellow

# URL de descarga directa para Windows
$ollamaUrl = "https://ollama.com/download/OllamaSetup.exe"
$downloadPath = "$env:TEMP\OllamaSetup.exe"

try {
    Write-Host "Descargando Ollama..." -ForegroundColor Cyan
    Invoke-WebRequest -Uri $ollamaUrl -OutFile $downloadPath
    
    Write-Host "Ejecutando instalador..." -ForegroundColor Cyan
    Start-Process -FilePath $downloadPath -Wait -Verb RunAs
    
    Write-Host "✅ Instalación completada" -ForegroundColor Green
} catch {
    Write-Host "❌ Error en la descarga automática" -ForegroundColor Red
    Write-Host "Descarga manual desde: https://ollama.com/download" -ForegroundColor Yellow
    Start-Process "https://ollama.com/download"
    Read-Host "Presiona Enter cuando hayas instalado Ollama manualmente"
}

# Paso 2: Verificar instalación y PATH
Write-Host "`n🔍 Paso 2: Verificando instalación..." -ForegroundColor Yellow

# Buscar ollama.exe en ubicaciones comunes
$possiblePaths = @(
    "C:\Users\$env:USERNAME\AppData\Local\Programs\Ollama\ollama.exe",
    "C:\Program Files\Ollama\ollama.exe",
    "C:\Program Files (x86)\Ollama\ollama.exe"
)

$ollamaPath = $null
foreach ($path in $possiblePaths) {
    if (Test-Path $path) {
        $ollamaPath = $path
        Write-Host "✅ Ollama encontrado en: $path" -ForegroundColor Green
        break
    }
}

if (-not $ollamaPath) {
    Write-Host "❌ No se encontró ollama.exe" -ForegroundColor Red
    Write-Host "Buscando en el sistema..." -ForegroundColor Yellow
    
    # Búsqueda más amplia
    try {
        $found = Get-ChildItem "C:\Users\$env:USERNAME\AppData\Local\Programs\" -Recurse -Filter "ollama.exe" -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($found) {
            $ollamaPath = $found.FullName
            Write-Host "✅ Ollama encontrado en: $ollamaPath" -ForegroundColor Green
        }
    } catch {
        Write-Host "❌ Error buscando Ollama" -ForegroundColor Red
        exit 1
    }
}

# Paso 3: Añadir al PATH si es necesario
Write-Host "`n🛠️ Paso 3: Configurando PATH..." -ForegroundColor Yellow

if ($ollamaPath) {
    $ollamaDir = Split-Path $ollamaPath -Parent
    $currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
    
    if ($currentPath -notlike "*$ollamaDir*") {
        Write-Host "Añadiendo Ollama al PATH del usuario..." -ForegroundColor Cyan
        $newPath = "$currentPath;$ollamaDir"
        [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
        
        # Actualizar PATH en la sesión actual
        $env:Path += ";$ollamaDir"
        Write-Host "✅ PATH actualizado" -ForegroundColor Green
    } else {
        Write-Host "✅ Ollama ya está en el PATH" -ForegroundColor Green
    }
}

# Paso 4: Verificar que funciona
Write-Host "`n✅ Paso 4: Verificando funcionamiento..." -ForegroundColor Yellow
try {
    $version = & $ollamaPath --version
    Write-Host "✅ Ollama funciona correctamente: $version" -ForegroundColor Green
} catch {
    Write-Host "❌ Error ejecutando Ollama" -ForegroundColor Red
    Write-Host "Intenta reiniciar PowerShell y ejecutar: ollama --version" -ForegroundColor Yellow
}

# Paso 5: Descargar modelo
Write-Host "`n🧠 Paso 5: Descargando modelo de IA..." -ForegroundColor Yellow
try {
    Write-Host "Descargando Llama 3.2 (3B)..." -ForegroundColor Cyan
    & $ollamaPath pull llama3.2:3b
    Write-Host "✅ Modelo descargado exitosamente" -ForegroundColor Green
} catch {
    Write-Host "❌ Error descargando modelo" -ForegroundColor Red
    Write-Host "Ejecuta manualmente: ollama pull llama3.2:3b" -ForegroundColor Yellow
}

# Paso 6: Iniciar servidor
Write-Host "`n🚀 Paso 6: Iniciando servidor..." -ForegroundColor Yellow
try {
    Write-Host "Iniciando servidor Ollama en segundo plano..." -ForegroundColor Cyan
    Start-Process -FilePath $ollamaPath -ArgumentList "serve" -WindowStyle Hidden
    Start-Sleep -Seconds 5
    
    # Verificar que el servidor responde
    $response = Invoke-RestMethod -Uri "http://localhost:11434/api/version" -Method Get -TimeoutSec 10
    Write-Host "✅ Servidor funcionando - Versión: $($response.version)" -ForegroundColor Green
} catch {
    Write-Host "❌ Error iniciando servidor" -ForegroundColor Red
    Write-Host "Ejecuta manualmente: ollama serve" -ForegroundColor Yellow
}

Write-Host "`n🎉 ¡INSTALACIÓN COMPLETADA!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host "✅ Ollama instalado en: $ollamaPath" -ForegroundColor Green
Write-Host "✅ PATH configurado correctamente" -ForegroundColor Green
Write-Host "✅ Servidor funcionando en puerto 11434" -ForegroundColor Green
Write-Host ""
Write-Host "📋 COMANDOS ÚTILES:" -ForegroundColor Cyan
Write-Host "- Verificar: ollama --version" -ForegroundColor White
Write-Host "- Iniciar servidor: ollama serve" -ForegroundColor White
Write-Host "- Listar modelos: ollama list" -ForegroundColor White
Write-Host "- Chat directo: ollama run llama3.2:3b" -ForegroundColor White
Write-Host ""
Write-Host "🔄 REINICIA POWERSHELL si 'ollama --version' no funciona" -ForegroundColor Yellow
Write-Host "📞 SOPORTE: julio@juliomalaga.me" -ForegroundColor Yellow
