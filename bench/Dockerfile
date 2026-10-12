# The bench: where Muse's commands run. bench.py itself is bind-mounted (compose.yaml), so a custom
# image only needs python3 to stand in for this one.
# libusb-1.0-0: USB tools need it (ESP-IDF's installer rejects its openocd without it).
FROM python:3.12-slim
RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates curl git procps libusb-1.0-0 \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /work
CMD ["python3", "-u", "/app/bench.py"]
