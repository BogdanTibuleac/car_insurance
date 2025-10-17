<#
Collects logs from all running containers and saves them to a timestamped file.
#>

Write-Host "📜  Collecting logs..." -ForegroundColor Yellow

try { docker compose version > $null 2>&1; $compose = "docker compose" }
catch { $compose = "docker-compose" }

$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$outFile = "logs_$stamp.txt"

& $compose logs > $outFile
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅  Logs saved to $outFile" -ForegroundColor Green
}
else {
    Write-Host "❌  Could not collect logs." -ForegroundColor Red
}
