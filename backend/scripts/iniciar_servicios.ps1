$backendDir = "C:\Users\carde\Desktop\HACKATEC_proyecto\backend"
Set-Location $backendDir

# Detener cualquier proceso previo en el puerto 8000
$conexiones = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
foreach ($c in $conexiones) {
    Stop-Process -Id $c.OwningProcess -Force -ErrorAction SilentlyContinue
}

# Iniciar Uvicorn en segundo plano persistente
Start-Process -FilePath "$backendDir\.venv\Scripts\python.exe" `
    -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000" `
    -WorkingDirectory $backendDir `
    -RedirectStandardOutput "$backendDir\uvicorn.log" `
    -RedirectStandardError "$backendDir\uvicorn_err.log" `
    -WindowStyle Hidden

Start-Sleep -Seconds 2

# Detener cualquier cloudflared previo
Get-Process -Name "cloudflared" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

# Iniciar Cloudflared en segundo plano persistente
Start-Process -FilePath "$backendDir\cloudflared.exe" `
    -ArgumentList "tunnel", "--url", "http://127.0.0.1:8000", "--logfile", "$backendDir\cloudflared.log" `
    -WorkingDirectory $backendDir `
    -WindowStyle Hidden

Start-Sleep -Seconds 4
Write-Output "Servicios iniciados correctamente."
