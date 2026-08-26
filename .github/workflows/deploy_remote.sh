#!/bin/bash
set -ex
echo "=== Deploy iniciado ==="
cd ~/Docker_compose
echo "=== Actualizando codigo ==="
git fetch origin main
git reset --hard origin/main
echo "=== Construyendo imagen ==="
docker compose build app-backend
echo "=== Levantando contenedor ==="
docker compose up -d --no-build app-backend
echo "=== Verificando ==="
docker compose ps app-backend
echo "=== Deploy completado ==="
