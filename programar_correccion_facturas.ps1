# Programar tarea para corregir estados de facturas
# Este script crea una tarea programada en Windows para ejecutar el script
# de corrección de estados de facturas cada 15 minutos

# Ruta al proyecto
$proyectoPath = "C:\Users\jjse7\Desktop\EV-Django-Project\electrolineras_project"
$scriptPath = Join-Path -Path $proyectoPath -ChildPath "corregir_facturas.py"
$pythonPath = "python"  # Asumiendo que Python está en el PATH

# Comando a ejecutar
$comando = "cd $proyectoPath && $pythonPath corregir_facturas.py"

# Crear la tarea programada
$taskName = "CorregirEstadosFacturas"
$taskDescription = "Tarea para corregir estados de facturas en la aplicación de electrolineras"

# Eliminar la tarea si ya existe
try {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
    Write-Host "La tarea existente ha sido eliminada."
} catch {
    # La tarea no existía, continuar
}

# Crear la acción
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -Command `"$comando`""

# Crear el disparador (cada 15 minutos)
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 15) -RepetitionDuration ([TimeSpan]::MaxValue)

# Configurar que la tarea se ejecute como el usuario actual
$principal = New-ScheduledTaskPrincipal -UserId ([System.Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType S4U -RunLevel Highest

# Crear la definición de la tarea
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# Registrar la tarea
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Description $taskDescription

Write-Host "Tarea programada '$taskName' creada con éxito."
Write-Host "Se ejecutará cada 15 minutos para corregir los estados de las facturas."
