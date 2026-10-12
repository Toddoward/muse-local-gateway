# Muse Local Gateway setup for Windows (Docker Desktop). Run in an elevated PowerShell.
# Picks the network mode, writes .env, starts the stack, prints what to tell Muse.
# Re-run any time: an existing .env is kept (delete it to choose again).
# ASCII only: Windows PowerShell reads .ps1 files as ANSI.
$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)

function Die($m) { Write-Host "ERROR: $m" -ForegroundColor Red; exit 1 }
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) { Die 'Docker Desktop is required: https://www.docker.com/products/docker-desktop/' }
docker compose version *> $null; if ($LASTEXITCODE) { Die 'Docker Compose v2 is required' }

if (Test-Path .env) {
  Write-Host 'Keeping existing .env (delete it to choose the mode again).'
} else {
  Write-Host @'
How far may Muse's shell (the bench) reach?
  1) isolated  - internet through a proxy only; your computer and LAN are blocked  (recommended)
  2) lan-allow - isolated, plus specific LAN devices you list (HTTP APIs: Shelly, Tasmota, ...)
  3) open      - your computer and the whole LAN, every protocol
'@
  $mode = Read-Host 'Choose [1]'; if (-not $mode) { $mode = '1' }
  $files = 'compose.yaml'; $lan = ''
  switch ($mode) {
    '1' { }
    '2' {
      $lan = Read-Host 'LAN device IPs, space-separated'
      foreach ($ip in ($lan -split '\s+' | Where-Object { $_ })) {
        if ($ip -notmatch '^\d{1,3}(\.\d{1,3}){3}(/\d{1,2})?$') { Die "not an IPv4 address: $ip" }
      }
    }
    '3' {
      Write-Host 'WARNING: in "open" mode, if Muse is ever tricked by a malicious web page or file (prompt injection),' -ForegroundColor Yellow
      Write-Host 'the shell it controls can reach your router admin page, NAS, and every service on this computer.' -ForegroundColor Yellow
      if ((Read-Host 'Type "open" to confirm') -ne 'open') { Die 'cancelled' }
      $files += ';compose.open.yaml'
    }
    default { Die 'choose 1, 2 or 3' }
  }
  if ((Read-Host 'Let the bench use USB serial boards (ESP32 etc.)? [y/N]') -eq 'y') {
    if (-not (Get-Command usbipd -ErrorAction SilentlyContinue)) { Die 'install usbipd-win first: winget install usbipd' }
    $files += ';compose.usb.yaml'
    # Watcher: hands ESP32-style boards to WSL as they appear. Every 5 min + IgnoreNew = a dead watcher comes back.
    $a = New-ScheduledTaskAction -Execute powershell.exe -Argument "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$PSScriptRoot\usb-attach.ps1`""
    $t1 = New-ScheduledTaskTrigger -AtLogOn
    $t2 = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes 5)
    $p = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Highest
    $s = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -ExecutionTimeLimit ([TimeSpan]::Zero) -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
    Register-ScheduledTask -TaskName muse-usb-attach -Action $a -Trigger $t1, $t2 -Principal $p -Settings $s -Force | Out-Null
    Start-ScheduledTask muse-usb-attach
    Write-Host 'Registered scheduled task muse-usb-attach.'
  }
  Write-Host 'Tailscale auth key: admin console -> Settings -> Keys -> Generate auth key,'
  Write-Host '  Reusable off, Tags: tag:muse-gw  (add the policy in examples/tailnet-acl.hujson first).'
  $sec = Read-Host 'Paste the key (input hidden)' -AsSecureString
  $key = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec))
  if (-not $key) { Die 'an auth key is required' }
  $env_ = "TS_AUTHKEY=$key`nTS_HOSTNAME=muse-gateway`nMUSE_SHARE=./shared`nLAN_ALLOW=$lan`nMAX_UPLOAD_MB=200`nCOMPOSE_FILE=$files`nCOMPOSE_PATH_SEPARATOR=;`n"
  [IO.File]::WriteAllText((Join-Path (Get-Location) '.env'), $env_)
  # Only you (and SYSTEM/Administrators) may read the key.
  icacls .env /inheritance:r /grant:r "${env:USERNAME}:F" /grant:r 'SYSTEM:F' /grant:r 'Administrators:F' | Out-Null
  Write-Host "Wrote .env (mode: $($files -replace ';', ' + '))"
}

New-Item -ItemType Directory -Force shared, tailscale-state | Out-Null
docker compose up -d --build
if ($LASTEXITCODE) { Die 'docker compose up failed' }

Write-Host 'Waiting for the tailnet address...'
$ip = $null
for ($i = 0; $i -lt 60 -and -not $ip; $i++) {
  $ip = (docker compose exec -T tailscale tailscale ip -4 2>$null | Select-Object -First 1)
  if (-not $ip) { Start-Sleep 2 }
}
if (-not $ip) { Die 'no tailnet address yet. Check: docker compose logs tailscale' }

Write-Host @"

Done. Send this to Muse:
----------------------------------------------------------------------
Install the muse-local-gateway skill from
https://github.com/Toddoward/muse-local-gateway (SKILL.md).
My gateway: files http://${ip}:8730, shell http://${ip}:8731
Run bin/gateway-check.sh ${ip}:8730 first.
----------------------------------------------------------------------
Then in the Tailscale admin console, tag the Muse device tag:muse.
Shared folder: $((Resolve-Path shared).Path)
"@
