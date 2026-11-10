<#
.SYNOPSIS
    Script de validación automatizada — Punto 4.b (Consumo desde PC Anfitrión Windows).

.DESCRIPTION
    Realiza una auditoría exhaustiva del ciclo de vida CRUD de la API REST Flask
    desplegada en AWS EC2 (VM1) utilizando Invoke-RestMethod nativo de PowerShell,
    garantizando compatibilidad estricta tanto en Windows PowerShell 5.1 como en PowerShell 7+.

.PARAMETER PublicIp
    Dirección IPv4 pública asignada a la instancia VM1 en AWS EC2.

.PARAMETER Port
    Puerto TCP donde escucha el servicio (5000 para Gunicorn nativo, 80 para Apache Proxy).

.EXAMPLE
    .\test_api_from_host.ps1 -PublicIp 3.85.120.45 -Port 5000
    .\test_api_from_host.ps1 -PublicIp 3.85.120.45 -Port 80
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [ValidatePattern('^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')]
    [string]$PublicIp,

    [Parameter(Mandatory = $false, Position = 1)]
    [ValidateRange(1, 65535)]
    [int]$Port = 5000
)

$ErrorActionPreference = "Continue"

$baseUrl = "http://${PublicIp}:${Port}"
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "AUDITORÍA PUNTO 4.b: Consumo de API REST desde Dispositivo Externo (Host)" -ForegroundColor Cyan
Write-Host "Destino evaluado: $baseUrl" -ForegroundColor Yellow
Write-Host "Fecha y hora:     $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
Write-Host "======================================================================" -ForegroundColor Cyan

$totalTests = 0
$passedTests = 0

function Assert-Endpoint {
    param(
        [string]$TestName,
        [string]$Method,
        [string]$Endpoint,
        [int]$ExpectedStatus,
        [object]$Body = $null
    )

    $script:totalTests++
    Write-Host -NoNewline "[$script:totalTests] $TestName ... "

    $uri = "${baseUrl}${Endpoint}"
    $params = @{
        Uri         = $uri
        Method      = $Method
        TimeoutSec  = 10
        ErrorAction = 'Stop'
    }

    if ($null -ne $Body) {
        $params.Body = ($Body | ConvertTo-Json -Compress)
        $params.ContentType = "application/json"
    }

    try {
        $response = Invoke-RestMethod @params
        if ($ExpectedStatus -ge 200 -and $ExpectedStatus -lt 300) {
            Write-Host "PASS (HTTP $ExpectedStatus)" -ForegroundColor Green
            $script:passedTests++
            return $response
        } else {
            Write-Host "FAIL (Se esperaba $ExpectedStatus pero respondió con éxito)" -ForegroundColor Red
            return $null
        }
    }
    catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        if ($null -eq $statusCode) {
            # En PowerShell Core / .NET 6+
            if ($_.Exception -match '(\d{3})') {
                $statusCode = [int]$matches[1]
            }
        }

        if ($statusCode -eq $ExpectedStatus) {
            Write-Host "PASS (HTTP $ExpectedStatus capturado correctamente)" -ForegroundColor Green
            $script:passedTests++
            return $_.ErrorDetails.Message
        } else {
            Write-Host "FAIL (Esperado: $ExpectedStatus | Obtenido: $statusCode | Error: $($_.Exception.Message))" -ForegroundColor Red
            return $null
        }
    }
}

# 1. Health-check
$health = Assert-Endpoint -TestName "GET /api/health (Verificar disponibilidad e IMDSv2)" `
                          -Method "GET" -Endpoint "/api/health" -ExpectedStatus 200
if ($null -ne $health) {
    Write-Host "   Instancia: $($health.ec2_metadata.instance_id) | AZ: $($health.ec2_metadata.availability_zone)" -ForegroundColor DarkGray
}

# 2. Listar productos
$products = Assert-Endpoint -TestName "GET /api/products (Listar colección de productos)" `
                            -Method "GET" -Endpoint "/api/products" -ExpectedStatus 200
if ($null -ne $products) {
    Write-Host "   Total de productos registrados: $($products.Count)" -ForegroundColor DarkGray
}

# 3. Crear producto vía POST
$newProductData = @{
    name        = "Mouse Inalámbrico Host Windows"
    description = "Auditado desde PowerShell anfitrión hacia AWS EC2"
    price       = 49.99
    stock       = 30
}

$createRes = Assert-Endpoint -TestName "POST /api/products (Crear nuevo producto en AWS)" `
                             -Method "POST" -Endpoint "/api/products" -ExpectedStatus 201 `
                             -Body $newProductData

$newId = $createRes.id

if ($null -ne $newId) {
    Write-Host "   ID generado: $newId" -ForegroundColor DarkGray

    # 4. Consultar producto creado
    $null = Assert-Endpoint -TestName "GET /api/products/$newId (Consultar producto creado)" `
                            -Method "GET" -Endpoint "/api/products/$newId" -ExpectedStatus 200

    # 5. Actualizar producto vía PUT
    $updateData = @{
        name  = "Mouse Inalámbrico Host Windows - Modificado"
        price = 59.99
        stock = 45
    }
    $null = Assert-Endpoint -TestName "PUT /api/products/$newId (Actualizar precio y stock)" `
                            -Method "PUT" -Endpoint "/api/products/$newId" -ExpectedStatus 200 `
                            -Body $updateData

    # 6. Eliminar producto vía DELETE
    $null = Assert-Endpoint -TestName "DELETE /api/products/$newId (Eliminar producto)" `
                            -Method "DELETE" -Endpoint "/api/products/$newId" -ExpectedStatus 200

    # 7. Validar que retorne 404 Not Found
    $null = Assert-Endpoint -TestName "GET /api/products/$newId (Verificar 404 tras eliminación)" `
                            -Method "GET" -Endpoint "/api/products/$newId" -ExpectedStatus 404
}

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "RESUMEN DE AUDITORÍA: $passedTests de $totalTests pruebas superadas." -ForegroundColor $(if ($passedTests -eq $totalTests) { "Green" } else { "Red" })
if ($passedTests -eq $totalTests) {
    Write-Host "RESULTADO: AUDITORÍA EXTERNA PUNTO 4.b 100% EXITOSA" -ForegroundColor Green
    exit 0
} else {
    Write-Host "RESULTADO: HUBO FALLAS EN LA AUDITORÍA" -ForegroundColor Red
    exit 1
}
