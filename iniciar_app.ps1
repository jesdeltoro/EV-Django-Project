# Script para iniciar la aplicación Django y el actualizador de baterías
Write-Host "Iniciando servidor Django..."
Start-Process -FilePath "python" -ArgumentList "electrolineras_project/manage.py", "runserver" -WorkingDirectory "c:\Users\jjse7\Desktop\EV-Django-Project\"
 
Write-Host "Iniciando actualizador de baterías..."
Start-Process -FilePath "python" -ArgumentList "electrolineras_project/manage.py", "actualizar_baterias", "--intervalo=30" -WorkingDirectory "c:\Users\jjse7\Desktop\EV-Django-Project\"

Write-Host "¡Aplicación iniciada con éxito!"
Write-Host "Presiona Ctrl+C y confirma para detener todos los procesos."

# Esperar a que el usuario presione teclas
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
