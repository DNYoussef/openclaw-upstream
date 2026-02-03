# OpenClaw Windows Development Guide

This directory contains PowerShell scripts for Windows development environments.

## Prerequisites

- Windows 10/11 with PowerShell 5.1+
- Node.js 22.12.0 or higher
- pnpm (installed via `npm install -g pnpm`)
- Docker Desktop for Windows (for container-based development)

## Quick Start

### Initial Setup

```powershell
# Install dependencies
pnpm install

# Set up git hooks
.\scripts\setup-git-hooks.ps1

# Build the project
pnpm build
```

### Development

```powershell
# Start development server (gateway)
.\scripts\dev-windows.ps1

# Start TUI in dev mode
.\scripts\dev-windows.ps1 -Mode tui

# Start with file watching
.\scripts\dev-windows.ps1 -Mode watch

# Reset and start fresh
.\scripts\dev-windows.ps1 -Reset
```

### Docker Development

```powershell
# Full Docker setup (build image + start gateway)
.\scripts\docker-setup.ps1

# Clean up Docker test resources
.\scripts\test-cleanup-docker.ps1
```

### Testing

```powershell
# Run unit tests
.\scripts\run-tests.ps1 -Suite unit

# Run with coverage
.\scripts\run-tests.ps1 -Suite unit -Coverage

# Run E2E tests
.\scripts\run-tests.ps1 -Suite e2e

# Run all tests (except Docker)
.\scripts\run-tests.ps1 -Suite all
```

## Available PowerShell Scripts

| Script | Description |
|--------|-------------|
| `docker-setup.ps1` | Build Docker image and start gateway |
| `dev-windows.ps1` | Start development server |
| `run-tests.ps1` | Run test suites |
| `setup-git-hooks.ps1` | Configure git pre-commit hooks |
| `test-cleanup-docker.ps1` | Clean up Docker test resources |
| `build-and-run-windows.ps1` | Build and run in one step |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENCLAW_CONFIG_DIR` | `~/.openclaw` | Configuration directory |
| `OPENCLAW_WORKSPACE_DIR` | `~/.openclaw/workspace` | Workspace directory |
| `OPENCLAW_GATEWAY_PORT` | `18789` | Gateway HTTP port |
| `OPENCLAW_BRIDGE_PORT` | `18790` | Bridge port |
| `OPENCLAW_PROFILE` | - | Set to `dev` for development mode |

## Notes

- Docker tests that use bash scripts may require WSL or Git Bash
- Some macOS-specific scripts (codesign, notarize) are not applicable on Windows
- For iOS/Android builds, use their respective native toolchains

## Troubleshooting

### PowerShell Execution Policy

If scripts won't run, you may need to adjust the execution policy:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Node.js Version

Ensure you're using Node.js 22.12.0+:

```powershell
node --version
# Should show v22.12.0 or higher
```

### pnpm Installation

If pnpm is not found:

```powershell
npm install -g pnpm@10
```
