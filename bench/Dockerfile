# The bench: where Muse's commands run. bench.py itself is bind-mounted (compose.yaml), so a forge or
# custom image only needs python3 to stand in for this one.
FROM python:3.12-slim
RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates curl git procps \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /work
CMD ["python3", "-u", "/app/bench.py"]
