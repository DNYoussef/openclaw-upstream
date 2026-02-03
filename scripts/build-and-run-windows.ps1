#Requires -Version 5.1
<#
.SYNOPSIS
    Build and run OpenClaw on Windows
.DESCRIPTION
    PowerShell equivalent of build-and-run-mac.sh for Windows environments.
.EXAMPLE
    .\build-and-run-windows.ps1
    .\build-and-run-windows.ps1 -SkipBuild
#>

[CmdletBinding()]
param(
    [Parameter()]
    [switch]$SkipBuild,

    [Parameter()]
    [switch]$Dev
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ROOT_DIR = Split-Path -Parent $PSScriptRoot

Push-Location $ROOT_DIR
try {
    if (-not $SkipBuild) {
        Write-Host "==> Building OpenClaw..." -ForegroundColor Cyan
        pnpm build
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Build failed"
            exit 1
        }
    }

    Write-Host "==> Starting OpenClaw..." -ForegroundColor Cyan
    if ($Dev) {
        $env:OPENCLAW_PROFILE = 'dev'
        pnpm start --dev gateway
    } else {
        pnpm start gateway
    }
} finally {
    Pop-Location
}
