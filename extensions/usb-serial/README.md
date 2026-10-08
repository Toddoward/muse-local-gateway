# USB-serial extension

Gives the gateway container access to USB serial devices — the dev
station for ESP32 work: build firmware, flash, watch serial logs.

## Linux (full support)

Add the device to `docker-compose.yml`:

```yaml
services:
  gateway:
    devices:
      - "/dev/ttyUSB0:/dev/ttyUSB0"
```

Find the port: `ls /dev/ttyUSB* /dev/ttyACM*`. Re-run
`docker compose up -d`. Muse can then ask the gateway to run the
toolchain (e.g. `idf.py flash`, `idf.py monitor`) against that port.

## Windows (via usbipd-win)

Docker Desktop cannot pass USB through directly:

1. Install [usbipd-win](https://github.com/dorssel/usbipd-win).
2. `usbipd list`, then `usbipd attach --wsl --busid <id>` to expose the
   device inside WSL2.
3. Add the `--device` entry as on Linux.

## macOS

Not available under Docker Desktop. Use a Linux box for this
extension.

## What Muse does with it

With the device visible in the container, Muse (via the gateway's shell,
or via a `system.run`-style command if the gateway offers one) can:

- build ESP32 firmware (`idf.py build`)
- flash it (`idf.py -p /dev/ttyUSB0 flash`)
- watch logs (`idf.py -p /dev/ttyUSB0 monitor`)

This is the **dev station** role: at runtime the flashed ESP32 talks to
Muse over Wi-Fi itself (see `../../gadgets/`). The container does not
proxy the device at runtime.
