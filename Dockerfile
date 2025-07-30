FROM python:3.13-slim AS package-builder

WORKDIR /app
COPY requirements.txt .
RUN apt update && apt install -y gcc && pip install --no-compile --no-cache-dir --user -r requirements.txt
COPY --from=devkitpro/devkitarm /opt/devkitpro/tools/bin/tex3ds /usr/local/bin/tex3ds

FROM python:3.13-slim AS runner

WORKDIR /app
COPY --from=package-builder /root/.local /root/.local
COPY --from=package-builder /usr/local/bin/tex3ds /usr/local/bin/tex3ds

COPY databases databases
COPY modules modules
COPY tools tools
COPY main.py .

CMD ["python", "main.py"]