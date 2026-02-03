#Requires -Version 5.1
<#
.SYNOPSIS
    OpenClaw Docker setup script for Windows
.DESCRIPTION
    PowerShell equivalent of docker-setup.sh for Windows environments.
    Sets up Docker containers for OpenClaw gateway.
.EXAMPLE
    .\docker-setup.ps1
.NOTES
    Requires Docker Desktop for Windows with docker compose support
#>

[CmdletBinding()]
param(
    [Parameter()]
    [string]$ImageName = $env:OPENCLAW_IMAGE,

    [Parameter()]
    [string]$ConfigDir = $env:OPENCLAW_CONFIG_DIR,

    [Parameter()]
    [string]$WorkspaceDir = $env:OPENCLAW_WORKSPACE_DIR,

    [Parameter()]
    [string]$ExtraMounts = $env:OPENCLAW_EXTRA_MOUNTS,

    [Parameter()]
    [string]$HomeVolumeName = $env:OPENCLAW_HOME_VOLUME
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Script root directory
$ROOT_DIR = Split-Path -Parent $PSScriptRoot
$COMPOSE_FILE = Join-Path $ROOT_DIR 'docker-compose.yml'
$EXTRA_COMPOSE_FILE = Join-Path $ROOT_DIR 'docker-compose.extra.yml'

# Set defaults
if (-not $ImageName) { $ImageName = 'openclaw:local' }
if (-not $ConfigDir) { $ConfigDir = Join-Path $env:USERPROFILE '.openclaw' }
if (-not $WorkspaceDir) { $WorkspaceDir = Join-Path $ConfigDir 'workspace' }

# Check for required commands
function Test-Command {
    param([string]$Command)
    $null -ne (Get-Command $Command -ErrorAction SilentlyContinue)
}

if (-not (Test-Command 'docker')) {
    Write-Error "Missing dependency: docker"
    exit 1
}

# Test docker compose
try {
    $null = docker compose version 2>$null
} catch {
    Write-Error "Docker Compose not available (try: docker compose version)"
    exit 1
}

# Create directories
if (-not (Test-Path $ConfigDir)) {
    New-Item -ItemType Directory -Path $ConfigDir -Force | Out-Null
}
if (-not (Test-Path $WorkspaceDir)) {
    New-Item -ItemType Directory -Path $WorkspaceDir -Force | Out-Null
}

# Set environment variables
$env:OPENCLAW_CONFIG_DIR = $ConfigDir
$env:OPENCLAW_WORKSPACE_DIR = $WorkspaceDir
$env:OPENCLAW_GATEWAY_PORT = if ($env:OPENCLAW_GATEWAY_PORT) { $env:OPENCLAW_GATEWAY_PORT } else { '18789' }
$env:OPENCLAW_BRIDGE_PORT = if ($env:OPENCLAW_BRIDGE_PORT) { $env:OPENCLAW_BRIDGE_PORT } else { '18790' }
$env:OPENCLAW_GATEWAY_BIND = if ($env:OPENCLAW_GATEWAY_BIND) { $env:OPENCLAW_GATEWAY_BIND } else { 'lan' }
$env:OPENCLAW_IMAGE = $ImageName
$env:OPENCLAW_DOCKER_APT_PACKAGES = if ($env:OPENCLAW_DOCKER_APT_PACKAGES) { $env:OPENCLAW_DOCKER_APT_PACKAGES } else { '' }
$env:OPENCLAW_EXTRA_MOUNTS = $ExtraMounts
$env:OPENCLAW_HOME_VOLUME = $HomeVolumeName

# Generate gateway token if not set
if (-not $env:OPENCLAW_GATEWAY_TOKEN) {
    # Use .NET for cryptographic random bytes
    $bytes = New-Object byte[] 32
    [System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
    $env:OPENCLAW_GATEWAY_TOKEN = [BitConverter]::ToString($bytes) -replace '-', '' | ForEach-Object { $_.ToLower() }
}

# Build compose args
$COMPOSE_FILES = @($COMPOSE_FILE)
$COMPOSE_ARGS = @()

function Write-ExtraCompose {
    param(
        [string]$HomeVolume,
        [string[]]$Mounts
    )

    $content = @"
services:
  openclaw-gateway:
    volumes:
"@

    if ($HomeVolume) {
        $content += "`n      - ${HomeVolume}:/home/node"
        $content += "`n      - ${ConfigDir}:/home/node/.openclaw"
        $content += "`n      - ${WorkspaceDir}:/home/node/.openclaw/workspace"
    }

    foreach ($mount in $Mounts) {
        $content += "`n      - $mount"
    }

    $content += @"

  openclaw-cli:
    volumes:
"@

    if ($HomeVolume) {
        $content += "`n      - ${HomeVolume}:/home/node"
        $content += "`n      - ${ConfigDir}:/home/node/.openclaw"
        $content += "`n      - ${WorkspaceDir}:/home/node/.openclaw/workspace"
    }

    foreach ($mount in $Mounts) {
        $content += "`n      - $mount"
    }

    if ($HomeVolume -and $HomeVolume -notmatch '/') {
        $content += @"

volumes:
  ${HomeVolume}:
"@
    }

    $content | Out-File -FilePath $EXTRA_COMPOSE_FILE -Encoding UTF8 -NoNewline
}

# Parse extra mounts
$VALID_MOUNTS = @()
if ($ExtraMounts) {
    $mounts = $ExtraMounts -split ','
    foreach ($mount in $mounts) {
        $mount = $mount.Trim()
        if ($mount) {
            $VALID_MOUNTS += $mount
        }
    }
}

if ($HomeVolumeName -or $VALID_MOUNTS.Count -gt 0) {
    Write-ExtraCompose -HomeVolume $HomeVolumeName -Mounts $VALID_MOUNTS
    $COMPOSE_FILES += $EXTRA_COMPOSE_FILE
}

foreach ($composeFile in $COMPOSE_FILES) {
    $COMPOSE_ARGS += '-f'
    $COMPOSE_ARGS += $composeFile
}

$COMPOSE_HINT = "docker compose " + ($COMPOSE_FILES | ForEach-Object { "-f $_" }) -join ' '

# Write/update .env file
$ENV_FILE = Join-Path $ROOT_DIR '.env'
$envVars = @{
    'OPENCLAW_CONFIG_DIR' = $ConfigDir
    'OPENCLAW_WORKSPACE_DIR' = $WorkspaceDir
    'OPENCLAW_GATEWAY_PORT' = $env:OPENCLAW_GATEWAY_PORT
    'OPENCLAW_BRIDGE_PORT' = $env:OPENCLAW_BRIDGE_PORT
    'OPENCLAW_GATEWAY_BIND' = $env:OPENCLAW_GATEWAY_BIND
    'OPENCLAW_GATEWAY_TOKEN' = $env:OPENCLAW_GATEWAY_TOKEN
    'OPENCLAW_IMAGE' = $ImageName
    'OPENCLAW_EXTRA_MOUNTS' = $ExtraMounts
    'OPENCLAW_HOME_VOLUME' = $HomeVolumeName
    'OPENCLAW_DOCKER_APT_PACKAGES' = $env:OPENCLAW_DOCKER_APT_PACKAGES
}

# Read existing env file and update
$existingEnv = @{}
if (Test-Path $ENV_FILE) {
    Get-Content $ENV_FILE | ForEach-Object {
        if ($_ -match '^([^=]+)=(.*)$') {
            $existingEnv[$matches[1]] = $matches[2]
        }
    }
}

foreach ($key in $envVars.Keys) {
    $existingEnv[$key] = $envVars[$key]
}

$existingEnv.GetEnumerator() | ForEach-Object {
    "$($_.Key)=$($_.Value)"
} | Out-File -FilePath $ENV_FILE -Encoding UTF8

# Build Docker image
Write-Host "==> Building Docker image: $ImageName" -ForegroundColor Cyan
$buildArgs = @(
    'build'
    '--build-arg', "OPENCLAW_DOCKER_APT_PACKAGES=$($env:OPENCLAW_DOCKER_APT_PACKAGES)"
    '-t', $ImageName
    '-f', (Join-Path $ROOT_DIR 'Dockerfile')
    $ROOT_DIR
)
& docker @buildArgs
if ($LASTEXITCODE -ne 0) {
    Write-Error "Docker build failed"
    exit 1
}

Write-Host ""
Write-Host "==> Onboarding (interactive)" -ForegroundColor Cyan
Write-Host "When prompted:"
Write-Host "  - Gateway bind: lan"
Write-Host "  - Gateway auth: token"
Write-Host "  - Gateway token: $($env:OPENCLAW_GATEWAY_TOKEN)"
Write-Host "  - Tailscale exposure: Off"
Write-Host "  - Install Gateway daemon: No"
Write-Host ""

& docker compose @COMPOSE_ARGS run --rm openclaw-cli onboard --no-install-daemon
if ($LASTEXITCODE -ne 0) {
    Write-Error "Onboarding failed"
    exit 1
}

Write-Host ""
Write-Host "==> Provider setup (optional)" -ForegroundColor Cyan
Write-Host "WhatsApp (QR):"
Write-Host "  $COMPOSE_HINT run --rm openclaw-cli providers login"
Write-Host "Telegram (bot token):"
Write-Host "  $COMPOSE_HINT run --rm openclaw-cli providers add --provider telegram --token <token>"
Write-Host "Discord (bot token):"
Write-Host "  $COMPOSE_HINT run --rm openclaw-cli providers add --provider discord --token <token>"
Write-Host "Docs: https://docs.openclaw.ai/providers"

Write-Host ""
Write-Host "==> Starting gateway" -ForegroundColor Cyan
& docker compose @COMPOSE_ARGS up -d openclaw-gateway

Write-Host ""
Write-Host "Gateway running with host port mapping." -ForegroundColor Green
Write-Host "Access from tailnet devices via the host's tailnet IP."
Write-Host "Config: $ConfigDir"
Write-Host "Workspace: $WorkspaceDir"
Write-Host "Token: $($env:OPENCLAW_GATEWAY_TOKEN)"
Write-Host ""
Write-Host "Commands:"
Write-Host "  $COMPOSE_HINT logs -f openclaw-gateway"
Write-Host "  $COMPOSE_HINT exec openclaw-gateway node dist/index.js health --token `"$($env:OPENCLAW_GATEWAY_TOKEN)`""
