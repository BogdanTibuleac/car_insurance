<#
Stops and removes all containers, images, and volumes for this stack.
#>

Write-Host "🧹  Cleaning up environment..." -ForegroundColor Red

try { docker compose version > $null 2>&1; $compose = "docker compose" }
catch { $compose = "docker-compose" }

& $compose down -v --remove-orphans
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅  Containers, images, and volumes removed." -ForegroundColor Green
}
else {
    Write-Host "❌  Cleanup failed." -ForegroundColor Red
}
