param(
    [switch]$NoBackend,
    [switch]$NoFrontend,
    [switch]$NoStreamlit,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$venvActivate = Join-Path $root ".venv\Scripts\Activate.ps1"

function Start-Component {
    param(
        [string]$Name,
        [string]$WorkingDirectory,
        [string]$Command,
        [bool]$UseVenv = $false
    )

    $bootstrap = @(
        "Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned"
        "Set-Location '$WorkingDirectory'"
    )

    if ($UseVenv -and (Test-Path $venvActivate)) {
        $bootstrap += "& '$venvActivate'"
    }

    $bootstrap += $Command
    $fullCommand = ($bootstrap -join "; ")

    if ($DryRun) {
        Write-Host "[DRY RUN] $Name"
        Write-Host "  Dir: $WorkingDirectory"
        Write-Host "  Cmd: $fullCommand"
        return
    }

    Start-Process -FilePath "powershell.exe" `
        -ArgumentList @("-NoExit", "-Command", $fullCommand) `
        -WorkingDirectory $WorkingDirectory | Out-Null

    Write-Host "Started: $Name"
}

Write-Host "Project root: $root"
if (-not (Test-Path $venvActivate)) {
    Write-Warning ".venv activation script not found at $venvActivate"
    Write-Warning "Python services may fail if dependencies are not installed globally."
}

if (-not $NoBackend) {
    Start-Component -Name "FastAPI backend" `
        -WorkingDirectory $root `
        -Command "uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000" `
        -UseVenv $true
}

if (-not $NoFrontend) {
    Start-Component -Name "Vite frontend" `
        -WorkingDirectory (Join-Path $root "frontend") `
        -Command "npm run dev"
}

if (-not $NoStreamlit) {
    Start-Component -Name "Streamlit dashboard" `
        -WorkingDirectory $root `
        -Command "streamlit run app/app.py" `
        -UseVenv $true
}

Write-Host ""
Write-Host "Quick checks:"
Write-Host "- Backend health: http://127.0.0.1:8000/health"
Write-Host "- Backend docs:   http://127.0.0.1:8000/docs"
Write-Host "- Frontend URL:   check the Vite terminal output (usually http://localhost:5173)"
