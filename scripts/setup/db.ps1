<#
scripts/setup/db.ps1
Database lifecycle driver for Django + PostgreSQL inside Docker Compose.

Usage:
  ./scripts/setup/db.ps1 -Migrate              # run makemigrations + migrate
  ./scripts/setup/db.ps1 -Backup               # backup Postgres to ./backups/backup-<db>-<ts>.sql
  ./scripts/setup/db.ps1 -Restore -File .\backups\backup-car_insurance-2025....sql
  ./scripts/setup/db.ps1 -Rebuild              # drop volumes, recreate db service, run migrations

Options:
  -Project <name>   Compose project (default: folder name)
#>

param(
    [switch]$Migrate,
    [switch]$Backup,
    [switch]$Restore,
    [string]$File,
    [switch]$Rebuild,
    [string]$Project
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-ProjectName {
    if ($Project) { return $Project }
    return Split-Path -Leaf (Get-Location)
}

function Get-ComposeParts {
    try {
        docker compose version > $null 2>&1
        return @{Exe = "docker"; Sub = @("compose") }
    }
    catch {
        docker-compose --version > $null 2>&1
        return @{Exe = "docker-compose"; Sub = @() }
    }
}

function Compose-Run {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Args)
    & $script:ComposeExe @script:ComposeSub @Args
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed ($LASTEXITCODE): $($script:ComposeExe) $($script:ComposeSub -join ' ') $($Args -join ' ')"
    }
}

$parts = Get-ComposeParts
$script:ComposeExe = $parts.Exe
$script:ComposeSub = $parts.Sub
$script:ProjectName = Get-ProjectName

# -- MIGRATE --
if ($Migrate) {
    Write-Host "Applying Django migrations..." -ForegroundColor Cyan
    Compose-Run -Args @("exec", "backend", "python", "manage.py", "makemigrations")
    Compose-Run -Args @("exec", "backend", "python", "manage.py", "migrate")
    Write-Host "Migrations complete." -ForegroundColor Green
    exit 0
}

# -- BACKUP --
if ($Backup) {
    $DbName = $env:POSTGRES_DB; if (-not $DbName) { $DbName = "car_insurance" }
    $User = $env:POSTGRES_USER; if (-not $User) { $User = "postgres" }
    $outDir = "backups"; if (!(Test-Path $outDir)) { New-Item -ItemType Directory $outDir | Out-Null }
    $stamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $file = Join-Path $outDir "backup-$DbName-$stamp.sql"

    Write-Host "Creating backup: $file" -ForegroundColor Yellow
    docker exec $(docker ps -qf "name=db") pg_dump -U $User -d $DbName > $file
    Write-Host "Backup complete." -ForegroundColor Green
    exit 0
}

# -- RESTORE --
if ($Restore) {
    if (-not $File) { throw "Provide -File <path_to_sql_dump>" }
    if (!(Test-Path $File)) { throw "File not found: $File" }
    $DbName = $env:POSTGRES_DB; if (-not $DbName) { $DbName = "car_insurance" }
    $User = $env:POSTGRES_USER; if (-not $User) { $User = "postgres" }

    Write-Host "Restoring database from $File..." -ForegroundColor Yellow
    Get-Content -Raw $File | docker exec -i $(docker ps -qf "name=db") psql -U $User -d $DbName
    Write-Host "Restore complete." -ForegroundColor Green
    exit 0
}

# -- REBUILD --
if ($Rebuild) {
    Write-Host "Rebuilding DB and Redis containers..." -ForegroundColor Red
    Compose-Run -Args @("rm", "-s", "-f", "-v", "db", "redis")
    Compose-Run -Args @("up", "-d", "--no-deps", "--force-recreate", "db", "redis")
    Write-Host "Applying migrations after rebuild..." -ForegroundColor Cyan
    Compose-Run -Args @("exec", "backend", "python", "manage.py", "migrate")
    Write-Host "Rebuild complete." -ForegroundColor Green
    exit 0
}

Write-Host "Nothing to do. Use one of: -Migrate | -Backup | -Restore -File X | -Rebuild" -ForegroundColor Yellow
