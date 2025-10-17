<#
Manually triggers the scheduled job that detects expired insurance policies.
Assumes you implemented a `detect_expired_policies` management command.
#>

Write-Host "🕒  Running expiry-detection job..." -ForegroundColor Cyan

try { docker compose version > $null 2>&1; $compose = "docker compose" }
catch { $compose = "docker-compose" }

& $compose exec backend python manage.py detect_expired_policies
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅  Expiry detection completed." -ForegroundColor Green
}
else {
    Write-Host "❌  Expiry detection failed. Check container logs." -ForegroundColor Red
}
