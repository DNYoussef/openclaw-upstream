#Requires -Version 5.1
<#
.SYNOPSIS
    Start OpenClaw development server on Windows
.DESCRIPTION
    PowerShell script for starting the development environment.
.PARAMETER Mode
    Development mode: gateway, tui, watch
.PARAMETER Reset
    Reset configuration before starting
.EXAMPLE
    .\dev-windows.ps1
    .\dev-windows.ps1 -Mode tui
    .\dev-windows.ps1 -Mode gateway -Reset
#>

[CmdletBinding()]
param(
    [Parameter()]
    [ValidateSet('gateway', 'tui', 'watch')]
    [string]$Mode = 'gateway',

    [Parameter()]
    [switch]$Reset,

    [Parameter()]
    [switch]$SkipChannels
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ROOT_DIR = Split-Path -Parent $PSScriptRoot

Push-Location $ROOT_DIR
try {
    # Set development environment
    $env:OPENCLAW_PROFILE = 'dev'

    if ($SkipChannels) {
        $env:OPENCLAW_SKIP_CHANNELS = '1'
    }

    switch ($Mode) {
        'gateway' {
            Write-Host "==> Starting gateway in dev mode..." -ForegroundColor Cyan
            if ($Reset) {
                pnpm gateway:dev:reset
            } else {
                pnpm gateway:dev
            }
        }
        'tui' {
            Write-Host "==> Starting TUI in dev mode..." -ForegroundColor Cyan
            pnpm tui:dev
        }
        'watch' {
            Write-Host "==> Starting gateway with file watching..." -ForegroundColor Cyan
            pnpm gateway:watch
        }
    }
} finally {
    Pop-Location
}
