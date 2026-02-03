#Requires -Version 5.1
<#
.SYNOPSIS
    Run OpenClaw test suites on Windows
.DESCRIPTION
    PowerShell script to run various test suites.
.PARAMETER Suite
    Test suite to run: unit, e2e, live, docker, all
.EXAMPLE
    .\run-tests.ps1 -Suite unit
    .\run-tests.ps1 -Suite all
#>

[CmdletBinding()]
param(
    [Parameter()]
    [ValidateSet('unit', 'e2e', 'live', 'docker', 'all')]
    [string]$Suite = 'unit',

    [Parameter()]
    [switch]$Coverage
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ROOT_DIR = Split-Path -Parent $PSScriptRoot

Push-Location $ROOT_DIR
try {
    switch ($Suite) {
        'unit' {
            Write-Host "==> Running unit tests..." -ForegroundColor Cyan
            if ($Coverage) {
                pnpm test:coverage
            } else {
                pnpm test
            }
        }
        'e2e' {
            Write-Host "==> Running E2E tests..." -ForegroundColor Cyan
            pnpm test:e2e
        }
        'live' {
            Write-Host "==> Running live tests..." -ForegroundColor Cyan
            $env:OPENCLAW_LIVE_TEST = '1'
            pnpm test:live
        }
        'docker' {
            Write-Host "==> Running Docker tests..." -ForegroundColor Cyan
            Write-Host "Note: Docker tests require WSL or Git Bash on Windows"

            # Run each Docker test via bash
            $dockerTests = @(
                'test:docker:live-models'
                'test:docker:live-gateway'
                'test:docker:onboard'
                'test:docker:gateway-network'
                'test:docker:qr'
                'test:docker:doctor-switch'
                'test:docker:plugins'
                'test:docker:cleanup'
            )

            foreach ($test in $dockerTests) {
                Write-Host "Running $test..." -ForegroundColor Yellow
                pnpm $test
                if ($LASTEXITCODE -ne 0) {
                    Write-Warning "$test failed"
                }
            }
        }
        'all' {
            Write-Host "==> Running all tests..." -ForegroundColor Cyan
            pnpm lint
            pnpm build
            pnpm test
            pnpm test:e2e
            $env:OPENCLAW_LIVE_TEST = '1'
            pnpm test:live
            Write-Host "Docker tests require manual execution via WSL"
        }
    }

    if ($LASTEXITCODE -eq 0) {
        Write-Host "==> Tests passed!" -ForegroundColor Green
    } else {
        Write-Host "==> Tests failed with exit code $LASTEXITCODE" -ForegroundColor Red
        exit $LASTEXITCODE
    }
} finally {
    Pop-Location
}
