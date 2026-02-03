#Requires -Version 5.1
<#
.SYNOPSIS
    Set up Git hooks for OpenClaw development on Windows
.DESCRIPTION
    PowerShell equivalent of the Node.js setup-git-hooks.js script.
    Configures pre-commit hooks for code formatting and linting.
.EXAMPLE
    .\setup-git-hooks.ps1
#>

[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ROOT_DIR = Split-Path -Parent $PSScriptRoot
$GIT_HOOKS_DIR = Join-Path $ROOT_DIR '.git\hooks'
$SOURCE_HOOKS_DIR = Join-Path $ROOT_DIR 'git-hooks'

if (-not (Test-Path $GIT_HOOKS_DIR)) {
    Write-Host "Creating .git/hooks directory..." -ForegroundColor Cyan
    New-Item -ItemType Directory -Path $GIT_HOOKS_DIR -Force | Out-Null
}

# Copy hooks from git-hooks directory
if (Test-Path $SOURCE_HOOKS_DIR) {
    Get-ChildItem -Path $SOURCE_HOOKS_DIR -File | ForEach-Object {
        $destPath = Join-Path $GIT_HOOKS_DIR $_.Name
        Copy-Item -Path $_.FullName -Destination $destPath -Force
        Write-Host "Installed hook: $($_.Name)" -ForegroundColor Green
    }
}

# Create pre-commit hook that runs format-staged
$preCommitPath = Join-Path $GIT_HOOKS_DIR 'pre-commit'
$preCommitContent = @'
#!/bin/sh
# Pre-commit hook for OpenClaw

# Run format-staged
node scripts/format-staged.js

# Exit with the status of format-staged
exit $?
'@

$preCommitContent | Out-File -FilePath $preCommitPath -Encoding UTF8 -NoNewline
Write-Host "Installed pre-commit hook" -ForegroundColor Green

Write-Host ""
Write-Host "Git hooks setup complete!" -ForegroundColor Cyan
Write-Host "Pre-commit hooks will run format-staged.js on each commit."
