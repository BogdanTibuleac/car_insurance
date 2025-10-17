<#
scripts/setup/run.ps1
Docker Compose management script for the Django Car Insurance backend.

Commands:
  run.ps1                 - Build images (using cache) and recreate containers
  run.ps1 -Rebuild        - Stop containers, remove volumes, rebuild images, start fresh
  run.ps1 -Start          - Recreate containers only (no build, use existing images)
  run.ps1 -Build          - Rebuild only the backend image and recreate its container (for code changes)
  -NoCache                - Disable build cache (force rebuild from scratch)

Examples:
  .\run.ps1               # Quick restart with cached build
  .\run.ps1 -Rebuild      # Full clean rebuild (with cache)
  .\run.ps1 -Start        # Quick container restart (no build)
  .\run.ps1 -Build        # Rebuild backend only (with cache)
  .\run.ps1 -Rebuild -NoCache  # Full rebuild without cache (when dependencies change)
#>

Param(
    [switch]$Rebuild,
    [switch]$Start,
    [switch]$Build,
    [switch]$NoCache
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Test-DockerRunning {
    Write-Host "Checking if Docker is running..." -ForegroundColor Blue
    $oldPreference = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        docker info > $null 2>&1
        if ($LASTEXITCODE -eq 0) { return $true }
        else { return $false }
    }
    catch { return $false }
    finally { $ErrorActionPreference = $oldPreference }
}

function Get-DockerComposeCommand {
    Write-Host "Detecting Docker Compose command..." -ForegroundColor Blue
    try {
        docker compose version | Out-Null
        return "docker compose"
    }
    catch {
        try {
            docker-compose --version | Out-Null
            return "docker-compose"
        }
        catch {
            return $null
        }
    }
}

if (-not (Test-DockerRunning)) {
    Write-Error "Docker daemon is not accessible. Start Docker (Desktop or Rancher Desktop) first."
    exit 1
}

$dockerComposeCmd = Get-DockerComposeCommand
if (-not $dockerComposeCmd) {
    Write-Error "Docker Compose is not available. Please install Docker Compose."
    exit 1
}

Write-Host "Using Docker Compose command: $dockerComposeCmd" -ForegroundColor Blue

try {
    if ($Rebuild) {
        Write-Host "REBUILD requested: removing containers and volumes" -ForegroundColor Yellow
        Invoke-Expression "$dockerComposeCmd down -v --remove-orphans"
        Write-Host "Building Docker images..." -ForegroundColor Yellow
        $buildCmd = "$dockerComposeCmd build"
        if ($NoCache) { $buildCmd += " --no-cache" }
        $buildCmd += " backend"
        Invoke-Expression $buildCmd
        Invoke-Expression "$dockerComposeCmd up -d"
    }
    elseif ($Start) {
        Write-Host "START requested: recreating containers only (no build)" -ForegroundColor Yellow
        Invoke-Expression "$dockerComposeCmd up -d --force-recreate --remove-orphans"
    }
    elseif ($Build) {
        Write-Host "BUILD requested: rebuilding backend image" -ForegroundColor Yellow
        Invoke-Expression "$dockerComposeCmd stop backend"
        $buildCmd = "$dockerComposeCmd build"
        if ($NoCache) { $buildCmd += " --no-cache" }
        $buildCmd += " backend"
        Invoke-Expression $buildCmd
        Invoke-Expression "$dockerComposeCmd up -d backend"
    }
    else {
        Write-Host "Default: rebuild images (using cache) and recreate containers" -ForegroundColor Yellow
        $buildCmd = "$dockerComposeCmd build backend"
        if ($NoCache) { $buildCmd += " --no-cache" }
        Invoke-Expression $buildCmd
        Invoke-Expression "$dockerComposeCmd up -d --force-recreate --remove-orphans"
    }

    # -------------------------------------------------------------------------------------
    # Django Database Setup (fully automated)
    # -------------------------------------------------------------------------------------
    Write-Host "Applying Django migrations..." -ForegroundColor Yellow
    Invoke-Expression "$dockerComposeCmd exec backend python manage.py makemigrations --noinput"
    Invoke-Expression "$dockerComposeCmd exec backend python manage.py migrate --noinput"

    Write-Host "Ensuring admin superuser exists..." -ForegroundColor Yellow
    $composeParts = $dockerComposeCmd -split ' '
    & $composeParts[0] $composeParts[1] exec backend python manage.py shell -c `
        "from django.contrib.auth.models import User;
u, created = User.objects.get_or_create(username='admin');
u.set_password('admin123');
u.is_superuser=True;
u.is_staff=True;
u.save()"
    # -------------------------------------------------------------------------------------

    Write-Host ""
    Write-Host "Django running at: http://localhost:8000" -ForegroundColor Green
    Write-Host "MailHog UI at: http://localhost:8025" -ForegroundColor Green
    Write-Host "Admin credentials: username='admin'  password='admin123'" -ForegroundColor Cyan
}
catch {
    Write-Host 'Error during requested action:' $_ -ForegroundColor Red
    exit 1
}
