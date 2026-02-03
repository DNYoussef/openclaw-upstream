#Requires -Version 5.1
<#
.SYNOPSIS
    Clean up Docker test resources
.DESCRIPTION
    PowerShell equivalent of test-cleanup-docker.sh for Windows environments.
    Removes test containers, networks, and volumes.
.EXAMPLE
    .\test-cleanup-docker.ps1
#>

[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Continue'

Write-Host "==> Cleaning up Docker test resources..." -ForegroundColor Cyan

# Stop and remove containers with openclaw prefix
$containers = docker ps -aq --filter "name=openclaw-test" 2>$null
if ($containers) {
    Write-Host "Stopping test containers..."
    docker stop $containers 2>$null
    docker rm -f $containers 2>$null
}

# Remove test networks
$networks = docker network ls --filter "name=openclaw-test" -q 2>$null
if ($networks) {
    Write-Host "Removing test networks..."
    foreach ($net in $networks) {
        docker network rm $net 2>$null
    }
}

# Remove test volumes
$volumes = docker volume ls --filter "name=openclaw-test" -q 2>$null
if ($volumes) {
    Write-Host "Removing test volumes..."
    foreach ($vol in $volumes) {
        docker volume rm $vol 2>$null
    }
}

Write-Host "==> Cleanup complete" -ForegroundColor Green
