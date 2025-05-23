# Script para instalar el servicio de actualización de baterías
# Requiere NSSM (Non-Sucking Service Manager) - https://nssm.cc/

# Directorio del proyecto
$proyectDir = "c:\Users\jjse7\Desktop\EV-Django-Project"

# Ruta al ejecutable de Python (asegúrate de que coincida con tu entorno)
$pythonPath = (Get-Command python).Source

# Verifica si NSSM está instalado
if (-not (Get-Command nssm -ErrorAction SilentlyContinue)) {
    Write-Host "Error: NSSM no está instalado. Por favor, descarga e instala NSSM primero." -ForegroundColor Red
    Write-Host "Puedes descargarlo desde: https://nssm.cc/download" -ForegroundColor Yellow
    exit 1
}

# Nombre del servicio
$serviceName = "EV_BatteryUpdater"

# Instalar el servicio
Write-Host "Instalando servicio '$serviceName'..." -ForegroundColor Cyan
nssm install $serviceName $pythonPath
nssm set $serviceName AppParameters "electrolineras_project\manage.py actualizar_baterias --intervalo=30"
nssm set $serviceName AppDirectory $proyectDir
nssm set $serviceName DisplayName "EV Battery Updater Service"
nssm set $serviceName Description "Servicio que actualiza automáticamente el porcentaje de batería de las electrolineras"
nssm set $serviceName Start SERVICE_AUTO_START
nssm set $serviceName ObjectName LocalSystem
nssm set $serviceName AppStdout "$proyectDir\logs\battery_updater.log"
nssm set $serviceName AppStderr "$proyectDir\logs\battery_updater_error.log"
nssm set $serviceName AppRotateFiles 1
nssm set $serviceName AppRotateOnline 1
nssm set $serviceName AppRotateSeconds 86400

# Crear directorio de logs si no existe
if (-not (Test-Path "$proyectDir\logs")) {
    New-Item -ItemType Directory -Path "$proyectDir\logs" | Out-Null
}

# Iniciar el servicio
Write-Host "Iniciando el servicio..." -ForegroundColor Green
Start-Service $serviceName

# Verificar el estado
$status = Get-Service $serviceName
Write-Host "Estado del servicio: $($status.Status)" -ForegroundColor Yellow

Write-Host "`nServicio instalado correctamente. El actualizador de baterías se ejecutará automáticamente al iniciar el sistema." -ForegroundColor Green
Write-Host "Para desinstalar el servicio, ejecuta: nssm remove $serviceName" -ForegroundColor Yellow
