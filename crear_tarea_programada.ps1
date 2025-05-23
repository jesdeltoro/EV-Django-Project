# Script para crear una tarea programada que ejecute el actualizador de baterías al iniciar sesión

$projectDir = "c:\Users\jjse7\Desktop\EV-Django-Project"
$taskName = "EV_ActualizarBaterias"
$pythonPath = (Get-Command python).Source

# Crear directorio de logs si no existe
if (-not (Test-Path "$projectDir\logs")) {
    New-Item -ItemType Directory -Path "$projectDir\logs" | Out-Null
}

# Crear un script batch que ejecutará el comando
$batchContent = @"
@echo off
echo Iniciando Actualizador de Baterias...
cd /d $projectDir
"$pythonPath" electrolineras_project\manage.py actualizar_baterias --intervalo=30 > "$projectDir\logs\battery_updater.log" 2>&1
"@

# Guardar el script batch
$batchPath = "$projectDir\actualizar_baterias.bat"
$batchContent | Out-File -FilePath $batchPath -Encoding ascii

# Crear la tarea programada
$action = New-ScheduledTaskAction -Execute $batchPath
$trigger = New-ScheduledTaskTrigger -AtLogon
$settings = New-ScheduledTaskSettingsSet -RunOnlyIfNetworkAvailable -WakeToRun -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Highest

# Registrar la tarea
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description "Ejecuta el actualizador de baterías para electrolineras" -Force

Write-Host "Tarea programada '$taskName' creada correctamente." -ForegroundColor Green
Write-Host "El actualizador de baterías se ejecutará automáticamente cuando inicies sesión." -ForegroundColor Yellow
Write-Host "Los logs se guardarán en: $projectDir\logs\battery_updater.log" -ForegroundColor Cyan
