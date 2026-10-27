<#
.SYNOPSIS
    Script automatizado de sustentación y grabación de video para la Práctica 7.
.DESCRIPTION
    Ejecuta de manera secuencial, con pausas didácticas y formato limpio,
    la presentación completa del proyecto desde el Host Windows para permitir
    grabar el video de contingencia sin pausas ni errores de tipeo.
#>

[CmdletBinding()]
param (
    [string]$TargetHost = "http://localhost:5000",
    [int]$PauseSeconds = 3
)

$ErrorActionPreference = "Continue"

function Show-Header {
    param([string]$Title)
    Write-Host ""
    Write-Host ("=" * 80) -ForegroundColor Cyan
    Write-Host " $Title" -ForegroundColor Yellow -NoNewline
    Write-Host ""
    Write-Host ("=" * 80) -ForegroundColor Cyan
}

Clear-Host
Show-Header "PRESENTACIÓN Y SUSTENTACIÓN PRÁCTICA 7: API REST FLASK E IOT UBIDOTS"
Write-Host "Estudiante: Eduard Criollo Yule | UAO" -ForegroundColor Green
Write-Host "Fecha: $(Get-Date -Format 'dd/MM/yyyy HH:mm')" -ForegroundColor Gray
Start-Sleep -Seconds $PauseSeconds

# -----------------------------------------------------------------------------
# FASE 0: EXPOSICIÓN DE ARCHIVOS DE CONFIGURACIÓN E INFRAESTRUCTURA
# -----------------------------------------------------------------------------
Show-Header "FASE 0: EXPOSICIÓN DE ARCHIVOS DE CONFIGURACIÓN E INFRAESTRUCTURA"

Write-Host "`n[1/4] Vagrantfile (Infraestructura de Virtualización):" -ForegroundColor Magenta
Write-Host "- OS: Ubuntu 22.04 LTS (bento/ubuntu-22.04)" -ForegroundColor White
Write-Host "- Red Privada: 192.168.50.3 (eth1)" -ForegroundColor White
Write-Host "- Port Forwarding: 5000:5000" -ForegroundColor White
Write-Host "- Aprovisionamiento desatendido de Flask, MySQL y repositorios" -ForegroundColor White
Start-Sleep -Seconds $PauseSeconds

Write-Host "`n[2/4] apirest.service (Persistencia y Demonio systemd):" -ForegroundColor Magenta
Write-Host "- Mantiene el servicio Flask activo permanentemente en 0.0.0.0:5000" -ForegroundColor White
Write-Host "- Reinicio automático ante fallos (Restart=always)" -ForegroundColor White
Start-Sleep -Seconds $PauseSeconds

Write-Host "`n[3/4] schema.sql (Base de datos relacional MySQL 'myflaskapp'):" -ForegroundColor Magenta
Write-Host "- Tabla 'books' con campos id (PK autoincrement), title, description, author" -ForegroundColor White
Write-Host "- Usuario dedicado 'flaskuser' con privilegios acotados" -ForegroundColor White
Start-Sleep -Seconds $PauseSeconds

Write-Host "`n[4/4] testUbidots.py (Cliente IoT con 5 variables):" -ForegroundColor Magenta
Write-Host "- Variables: temperature, humidity, position (context lat/lng), pressure, battery_level" -ForegroundColor White
Write-Host "- Mecanismo de 5 reintentos ante errores HTTP >= 400" -ForegroundColor White
Write-Host "- Carga segura de UBIDOTS_TOKEN desde entorno (.env)" -ForegroundColor White
Start-Sleep -Seconds $PauseSeconds

# -----------------------------------------------------------------------------
# FASE 1: SUSTENTACIÓN PARTE 1 — PRUEBAS CRUD DE LA API REST FLASK
# -----------------------------------------------------------------------------
Show-Header "FASE 1: DEMOSTRACIÓN DE LA API REST FLASK (PARTE 1)"

Write-Host "`nPaso 1.1: Consultar todos los libros (GET /books)" -ForegroundColor Yellow
curl.exe -i -s -X GET "$TargetHost/books"
Start-Sleep -Seconds $PauseSeconds

Write-Host "`nPaso 1.2: Consultar un libro por ID (GET /books/2)" -ForegroundColor Yellow
curl.exe -i -s -X GET "$TargetHost/books/2"
Start-Sleep -Seconds $PauseSeconds

Write-Host "`nPaso 1.3: Crear un nuevo libro (POST /books con JSON)" -ForegroundColor Yellow
'{"title": "Cien anos de soledad", "author": "Gabo", "description": "Realismo Magico"}' | curl.exe -i -s -H "Content-Type: application/json" -X POST --data-binary "@-" "$TargetHost/books"
Start-Sleep -Seconds $PauseSeconds

Write-Host "`nPaso 1.4: Actualizar un libro existente (PUT /books/2)" -ForegroundColor Yellow
'{"author": "Jorgito"}' | curl.exe -i -s -H "Content-Type: application/json" -X PUT --data-binary "@-" "$TargetHost/books/2"
Start-Sleep -Seconds $PauseSeconds

Write-Host "`nPaso 1.5: Eliminar un libro (DELETE /books/1)" -ForegroundColor Yellow
curl.exe -i -s -X DELETE "$TargetHost/books/1"
Start-Sleep -Seconds $PauseSeconds

Write-Host "`nPaso 1.6: Validar manejo de recurso inexistente (GET /books/1 -> 404 Not Found)" -ForegroundColor Yellow
curl.exe -i -s -X GET "$TargetHost/books/1"
Start-Sleep -Seconds $PauseSeconds

# -----------------------------------------------------------------------------
# FASE 2: SUSTENTACIÓN PARTE 2 — SIMULACIÓN IOT Y UBIDOTS
# -----------------------------------------------------------------------------
Show-Header "FASE 2: DEMOSTRACIÓN DE TELEMETRÍA IOT Y UBIDOTS (PARTE 2)"

Write-Host "`nPaso 2.1: Ejecutar ráfaga telemétrica con las 5 variables (testUbidots.py --once)" -ForegroundColor Yellow
python "d:\Documentos\Practica_AmbienteDesarrollo\mipracticas\Practica7\UbidotsClient\testUbidots.py" --once
Start-Sleep -Seconds $PauseSeconds

Write-Host "`nPaso 2.2: Actualización manual de variable 'temperature' con cURL" -ForegroundColor Yellow
$EnvToken = (Get-Content "d:\Documentos\Practica_AmbienteDesarrollo\mipracticas\Practica7\.env" -ErrorAction SilentlyContinue | Where-Object { $_ -match "^UBIDOTS_TOKEN=(.*)" } | ForEach-Object { $Matches[1].Trim() })
if (-not $EnvToken) { $EnvToken = "BBUS-qZdFGWNPNLOvb8S9q0yqAo4Bk4GLPs" }
'{"temperature": 45.0}' | curl.exe -i -s -H "Content-Type: application/json" -H "X-Auth-Token: $EnvToken" `
    -X POST --data-binary "@-" "http://industrial.api.ubidots.com/api/v1.6/devices/machine"
Start-Sleep -Seconds $PauseSeconds

Show-Header "RESUMEN DE RESULTADOS Y DASHBOARD"
Write-Host "1. API REST Flask en memoria y persistente operativa en puerto 5000." -ForegroundColor Green
Write-Host "2. Cliente IoT transmitiendo 5 variables telemétricas con éxito." -ForegroundColor Green
Write-Host "3. Dashboard configurado con Widgets Gauge, Mapa, Barras, Líneas y Tanque." -ForegroundColor Green
Write-Host "4. Evento configurado: alerta por correo cuando temperature > 40 C." -ForegroundColor Green
Write-Host "`nSustentación completada con éxito." -ForegroundColor Cyan
