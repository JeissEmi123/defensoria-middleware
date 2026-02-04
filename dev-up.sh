#!/bin/bash
set -euo pipefail

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker no esta instalado. Instala Docker Desktop o Docker Engine."
  exit 1
fi

if docker compose version >/dev/null 2>&1; then
  COMPOSE="docker compose"
elif command -v docker-compose >/dev/null 2>&1; then
  COMPOSE="docker-compose"
else
  echo "Docker esta instalado pero falta docker compose."
  echo "Instala Docker Desktop o el plugin docker-compose."
  exit 1
fi

if [ ! -f .env.docker ]; then
  echo "Falta .env.docker. Revisa el repositorio o crea el archivo."
  exit 1
fi

$COMPOSE up -d --build

echo "API disponible en http://localhost:9000"
echo "Health check: curl http://localhost:9000/health"
