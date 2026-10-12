# Runs on the Windows host (scheduled task "muse-usb-attach" from setup.ps1: at logon + every 5 min).
# Hands ESP32-style USB serial devices to WSL as they appear, so the bench container sees
# them as /dev/ttyACM* or /dev/ttyUSB* (with compose.usb.yaml). Re-attaches after a board resets and re-enumerates.
#   303a = Espressif native USB (C3/C5/C6/S3/H2 ...), 10c4 = CP210x, 1a86 = CH34x, 0403 = FTDI
# CAUTION: these chips also sit in Zigbee sticks, 3D printers, etc. Anything with these VIDs
# plugged into this PC leaves Windows and goes to the bench.
# ASCII only: Windows PowerShell reads .ps1 as ANSI.
$vids = '303a', '10c4', '1a86', '0403'
$log = Join-Path $PSScriptRoot 'usb-attach.log'
while ($true) {
    try {
        foreach ($d in (usbipd state | ConvertFrom-Json).Devices) {
            if (-not $d.BusId -or $d.ClientIPAddress) { continue }  # unplugged, or already attached
            if ($d.InstanceId -notmatch 'VID_([0-9A-Fa-f]{4})') { continue }
            if ($vids -notcontains $Matches[1].ToLower()) { continue }
            if (-not $d.PersistedGuid) { usbipd bind --busid $d.BusId 2>&1 | Out-Null }
            # The WSL kernel has these as modules and nothing (no udev) loads them on plug-in.
            # Idempotent; also covers a Docker Desktop restart, which brings up a fresh VM.
            wsl -d docker-desktop -u root modprobe -a vhci_hcd cdc_acm cp210x ch341 ftdi_sio 2>&1 | Out-Null
            $out = usbipd attach --wsl --busid $d.BusId 2>&1
            Add-Content $log "$(Get-Date -Format s) attach $($d.BusId) $($d.Description): $out"
        }
    } catch {
        Add-Content $log "$(Get-Date -Format s) error: $_"
    }
    Start-Sleep 2
}
