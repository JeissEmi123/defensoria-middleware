#!/bin/bash
set -euo pipefail

OS_NAME="$(uname -s)"
MISSING=0

check_cmd() {
  local cmd="$1"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "Falta: $cmd"
    MISSING=1
  fi
}

check_cmd git
check_cmd docker

if ! docker compose version >/dev/null 2>&1 && ! command -v docker-compose >/dev/null 2>&1; then
  echo "Falta: docker compose"
  MISSING=1
fi

if [ "$MISSING" -eq 0 ]; then
  echo "OK. Git y Docker estan instalados."
  exit 0
fi

echo ""
echo "Instalacion sugerida segun sistema operativo:"

case "$OS_NAME" in
  Darwin)
    echo "macOS (Homebrew):"
    echo "  brew install git"
    echo "  brew install --cask docker"
    ;;
  Linux)
    echo "Ubuntu/Debian:"
    echo "  sudo apt-get update"
    echo "  sudo apt-get install -y git docker.io docker-compose-plugin"
    echo ""
    echo "Fedora:"
    echo "  sudo dnf install -y git docker docker-compose-plugin"
    ;;
  MINGW*|MSYS*|CYGWIN*)
    echo "Windows (winget):"
    echo "  winget install Git.Git"
    echo "  winget install Docker.DockerDesktop"
    ;;
  *)
    echo "Sistema no reconocido. Instala Git y Docker manualmente."
    ;;
esac

echo ""
echo "Luego inicia Docker Desktop (si aplica) y vuelve a ejecutar:"
echo "  ./bootstrap.sh"
exit 1
