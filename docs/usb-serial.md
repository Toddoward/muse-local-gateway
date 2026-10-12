[![English](https://img.shields.io/badge/lang-English-111111?style=flat-square)](usb-serial.md)
[![한국어](https://img.shields.io/badge/lang-%ED%95%9C%EA%B5%AD%EC%96%B4-lightgrey?style=flat-square)](usb-serial.kr.md)

# USB serial boards

Lets Muse build, flash and read boards plugged into your computer (ESP32 family, ESP8266, any
USB-serial device). Turned on by answering **y** to the USB question in setup, which adds
`compose.usb.yaml`.

**How it stays safe:** the bench gets `/dev` so boards that reset and re-enumerate show up again,
but cgroup rules allow **only** serial devices (`ttyACM` 166, `ttyUSB` 188). Disks, `/dev/mem`
and everything else stay denied.

## Linux

Works directly. Plug the board in; it appears as `/dev/ttyACM0` or `/dev/ttyUSB0` in the bench.

## Windows

Docker Desktop can't see Windows USB devices. Setup uses [usbipd-win](https://github.com/dorssel/usbipd-win)
(`winget install usbipd`) and registers the scheduled task **`muse-usb-attach`**
(`setup/usb-attach.ps1`, at logon + every 5 minutes), which:

- hands boards with known USB IDs to WSL as they appear: `303a` Espressif native USB, `10c4` CP210x,
  `1a86` CH34x, `0403` FTDI;
- loads the serial drivers (`cdc_acm cp210x ch341 ftdi_sio`) — Docker Desktop's VM has no udev,
  and after a VM restart usbipd re-attaches boards **without** them;
- re-attaches a board after it resets.

> **Caution:** the same USB chips sit in Zigbee sticks, 3D printers and some keyboards' programming
> ports. Anything with those IDs leaves Windows and goes to the bench. Edit `$vids` in
> `setup/usb-attach.ps1` to narrow it. Log: `setup/usb-attach.log`.

## macOS

Not possible with Docker Desktop. Use a Linux machine (a Raspberry Pi works) for USB work.

## Which device name?

| Board | Connection | Shows up as |
|---|---|---|
| ESP32-S3 / C3 / C6 (USB port) | native USB | `/dev/ttyACM0` |
| ESP32 DevKit, ESP8266 (NodeMCU, D1 mini) | CP210x / CH340 bridge | `/dev/ttyUSB0` |

## Troubleshooting

- **Nothing appears, not even in Windows Device Manager:** a charge-only cable. Try another.
- **Windows sees it, the bench doesn't:** `usbipd list` should say *Attached*. Then
  `docker compose exec bench ls /dev/ttyACM* /dev/ttyUSB*`. If attached but missing, wait 30 s
  (driver reload) or restart the `muse-usb-attach` task.
- **Serial monitor hangs:** there is no TTY. Use
  `stty -F /dev/ttyUSB0 115200 raw -echo; timeout 10 cat /dev/ttyUSB0`.
