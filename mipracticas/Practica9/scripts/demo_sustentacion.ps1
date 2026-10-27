<#
.SYNOPSIS
    Script automatizado de sustentación para la Práctica 9 desde Windows PowerShell.
.DESCRIPTION
    Ejecuta secuencialmente las pruebas de los Ejercicios 1 a 6 (Usuarios, Persistencia,
    Productos y Despliegue en Apache WSGI) desde el anfitrión Windows.
#>

[CmdletBinding()]
param (
    [string]$FlaskHost = "http://localhost:5000",
    [string]$ApacheHost = "http://localhost:8080",
    [int]$PauseSeconds = 3
)

$ErrorActionPreference = "Continue"

function Show-Header {
    param([string]$Title)
    Write-Host ""
    Write-Host ("=" * 82) -ForegroundColor Cyan
    Write-Host " $Title" -ForegroundColor Yellow
    Write-Host ("=" * 82) -ForegroundColor Cyan
}

Clear-Host
Show-Header "SUSTENTACIÓN PRÁCTICA 9: FLASK + REST + MYSQL + GESTIÓN DE PRODUCTOS + APACHE WSGI"
Write-Host "Estudiante: Eduard Criollo Yule | Universidad Autónoma de Occidente" -ForegroundColor Green
Write-Host "Fecha: $(Get-Date -Format 'dd/MM/yyyy HH:mm')" -ForegroundColor Gray
Start-Sleep -Seconds $PauseSeconds

# -----------------------------------------------------------------------------
# FASE 1: EJERCICIO 3.a — PRUEBAS CRUD DE USUARIOS (/api/users)
# -----------------------------------------------------------------------------
Show-Header "FASE 1: PRUEBAS CRUD DE LA API REST DE USUARIOS (/api/users)"

Write-Host "`n[1.1] Listar todos los usuarios (GET /api/users)" -ForegroundColor Yellow
curl.exe -i -s -X GET "$FlaskHost/api/users"
Start-Sleep -Seconds $PauseSeconds

Write-Host "`n[1.2] Consultar usuario por ID (GET /api/users/1)" -ForegroundColor Yellow
curl.exe -i -s -X GET "$FlaskHost/api/users/1"
Start-Sleep -Seconds $PauseSeconds

Write-Host "`n[1.3] Crear nuevo usuario en MySQL (POST /api/users)" -ForegroundColor Yellow
curl.exe --% -i -s -H "Content-Type: application/json" -X POST -d "{\"name\":\"Eduard Criollo\",\"email\":\"eduard.criollo@uao.edu.co\",\"username\":\"ecriollo\",\"password\":\"789\"}" http://localhost:5000/api/users
Start-Sleep -Seconds $PauseSeconds

Write-Host "`n[1.4] Actualizar usuario existente (PUT /api/users/2)" -ForegroundColor Yellow
curl.exe --% -i -s -H "Content-Type: application/json" -X PUT -d "{\"name\":\"Maria Fernanda\",\"email\":\"maria.fernanda@gmail.com\",\"username\":\"mariaf\",\"password\":\"456\"}" http://localhost:5000/api/users/2
Start-Sleep -Seconds $PauseSeconds

Write-Host "`n[1.5] Eliminar usuario (DELETE /api/users/3)" -ForegroundColor Yellow
curl.exe -i -s -X DELETE "$FlaskHost/api/users/3"
Start-Sleep -Seconds $PauseSeconds

# -----------------------------------------------------------------------------
# FASE 2: EJERCICIO 5.b — PRUEBAS CRUD DE PRODUCTOS (/api/products)
# -----------------------------------------------------------------------------
Show-Header "FASE 2: PRUEBAS CRUD DE LA API REST DE PRODUCTOS (/api/products)"

Write-Host "`n[2.1] Listar catálogo de productos (GET /api/products)" -ForegroundColor Yellow
curl.exe -i -s -X GET "$FlaskHost/api/products"
Start-Sleep -Seconds $PauseSeconds

Write-Host "`n[2.2] Consultar producto por ID (GET /api/products/1)" -ForegroundColor Yellow
curl.exe -i -s -X GET "$FlaskHost/api/products/1"
Start-Sleep -Seconds $PauseSeconds

Write-Host "`n[2.3] Crear nuevo producto en MySQL (POST /api/products)" -ForegroundColor Yellow
curl.exe --% -i -s -H "Content-Type: application/json" -X POST -d "{\"name\":\"Mouse Inalambrico Pro\",\"description\":\"Sensor optico 25K DPI\",\"price\":79.99,\"stock\":30}" http://localhost:5000/api/products
Start-Sleep -Seconds $PauseSeconds

Write-Host "`n[2.4] Actualizar producto existente (PUT /api/products/2)" -ForegroundColor Yellow
curl.exe --% -i -s -H "Content-Type: application/json" -X PUT -d "{\"name\":\"Monitor UltraWide 34 HDR\",\"description\":\"Monitor curvo WQHD IPS 165Hz\",\"price\":510.00,\"stock\":12}" http://localhost:5000/api/products/2
Start-Sleep -Seconds $PauseSeconds

Write-Host "`n[2.5] Eliminar producto (DELETE /api/products/4)" -ForegroundColor Yellow
curl.exe -i -s -X DELETE "$FlaskHost/api/products/4"
Start-Sleep -Seconds $PauseSeconds

# -----------------------------------------------------------------------------
# FASE 3: EJERCICIO 6 — VERIFICACIÓN DE DESPLIEGUE EN APACHE2 + MOD_WSGI
# -----------------------------------------------------------------------------
Show-Header "FASE 3: VERIFICACIÓN DE DESPLIEGUE EN APACHE2 + MOD_WSGI (EJERCICIO 6)"

Write-Host "`n[3.1] Consultar /api/users a través de Apache2 WSGI ($ApacheHost/api/users)" -ForegroundColor Yellow
curl.exe -i -s -X GET "$ApacheHost/api/users"
Start-Sleep -Seconds $PauseSeconds

Write-Host "`n[3.2] Consultar /api/products a través de Apache2 WSGI ($ApacheHost/api/products)" -ForegroundColor Yellow
curl.exe -i -s -X GET "$ApacheHost/api/products"
Start-Sleep -Seconds $PauseSeconds

Show-Header "RESUMEN DE SUSTENTACIÓN COMPLETADO"
Write-Host "1. Base de datos MySQL 8.0 'myflaskapp' con tablas 'users' y 'products' persistentes." -ForegroundColor Green
Write-Host "2. API REST CRUD completa para Usuarios (/api/users) y Productos (/api/products)." -ForegroundColor Green
Write-Host "3. Plantillas web HTML/JS operativas para gestión de Usuarios y Productos." -ForegroundColor Green
Write-Host "4. Sitio web y API desplegados en Apache2 mediante libapache2-mod-wsgi-py3." -ForegroundColor Green
