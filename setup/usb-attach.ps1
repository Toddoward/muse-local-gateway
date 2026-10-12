# Runs on the Windows host (scheduled task "muse-usb-attach" from setup.ps1: at logon + every 5 min).
# Hands ESP32-style USB serial devices to WSL as they appear, so the bench container sees
# them as /dev/ttyACM* or /dev/ttyUSB* (with compose.usb.yaml). Re-attaches after a board resets and re-enumerates.
#   303a = Espressif native USB (C3/C5/C6/S3/H2 ...), 10c4 = CP210x, 1a86 = CH34x, 0403 = FTDI
# CAUTION: these chips also sit in Zigbee sticks, 3D printers, etc. Anything with these VIDs
# plugged into this PC leaves Windows and goes to the bench.
# ASCII only: Windows PowerShell reads .ps1 as ANSI.
$vids = '303a', '10c4', '1a86', '0403'
$log = Join-Path $PSScriptRoot 'usb-attach.log'
$lastLoad = [datetime]::MinValue
while ($true) {
    try {
        $devs = @((usbipd state | ConvertFrom-Json).Devices | Where-Object {
            $_.BusId -and $_.InstanceId -match 'VID_([0-9A-Fa-f]{4})' -and $vids -contains $Matches[1].ToLower() })
        # The WSL kernel has the serial drivers as modules and nothing (no udev) loads them.
        # Load them while any board is present, not only right before attaching: when the WSL VM
        # restarts (Docker Desktop restart, reboot), usbipd re-attaches boards WITHOUT the drivers.
        # Idempotent; throttled to every 30 s because each call starts a wsl process.
        if ($devs.Count -and ((Get-Date) - $lastLoad).TotalSeconds -ge 30) {
            wsl -d docker-desktop -u root modprobe -a vhci_hcd cdc_acm cp210x ch341 ftdi_sio 2>&1 | Out-Null
            $lastLoad = Get-Date
        }
        foreach ($d in $devs) {
            if ($d.ClientIPAddress) { continue }  # already attached
            if (-not $d.PersistedGuid) { usbipd bind --busid $d.BusId 2>&1 | Out-Null }
            $out = usbipd attach --wsl --busid $d.BusId 2>&1
            Add-Content $log "$(Get-Date -Format s) attach $($d.BusId) $($d.Description): $out"
        }
    } catch {
        Add-Content $log "$(Get-Date -Format s) error: $_"
    }
    Start-Sleep 2
}
