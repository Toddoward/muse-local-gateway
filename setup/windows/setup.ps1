# Local Gateway one-command setup for Windows.
# Run in an elevated PowerShell. Installs the container module (recommended).
# Requires: Docker Desktop, Tailscale for Windows.

$ErrorActionPreference = "Stop"

function Need($cmd, $hint) {
  if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
    Write-Host "missing: $cmd — $hint"
    exit 1
  }
}

Need "docker" "install Docker Desktop: https://www.docker.com/products/docker-desktop/"
Need "tailscale" "install Tailscale: https://tailscale.com/download/windows"

$skillDir = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
Set-Location (Join-Path $skillDir "modules\container")

New-Item -ItemType Directory -Force -Path "shared" | Out-Null
New-Item -ItemType Directory -Force -Path "tailscale-state" | Out-Null

Write-Host "==> starting gateway + tailscale sidecar"
docker compose up -d

Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Join the tailnet if prompted."
Write-Host "  2. Find the tailnet IP and share <tailnet-ip>:8730 with Muse."
Write-Host "  3. USB devices: Docker Desktop cannot pass USB through directly."
Write-Host "     Use usbipd-win to attach the USB device to WSL2, then add a"
Write-Host "     --device entry (see ../../extensions/usb-serial/)."
