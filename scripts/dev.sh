#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"
cd "$ROOT_DIR"

PY=python3
VENV="$ROOT_DIR/.venv"

create_venv() {
  if [ -d "$VENV" ] && [ ! -f "$VENV/bin/activate" ]; then
    echo "[dev] Found broken venv directory. Removing..."
    rm -rf "$VENV"
  fi

  if [ ! -d "$VENV" ]; then
    echo "[dev] Creating virtualenv..."
    if $PY -m venv "$VENV" 2>/dev/null && [ -f "$VENV/bin/activate" ]; then
      echo "[dev] venv created"
      return 0
    else
      echo "[dev] venv creation failed (ensurepip missing). Will fallback to system pip with --break-system-packages"
      return 1
    fi
  fi

  if [ -f "$VENV/bin/activate" ]; then
    return 0
  else
    return 1
  fi
}

install_deps_in_venv() {
  # shellcheck disable=SC1091
  source "$VENV/bin/activate"
  pip install -U pip
  pip install -r backend/requirements.txt
}

install_deps_system() {
  echo "[dev] Installing deps to system pip (PEP668 override)..."
  pip3 install -U pip --break-system-packages || true
  pip3 install -r backend/requirements.txt --break-system-packages
}

run_tests() {
  echo "[dev] Running tests..."
  $PY -m pytest -q || true
}

start_server() {
  echo "[dev] Starting server on http://127.0.0.1:8000 ..."
  exec $PY -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
}

if create_venv; then
  install_deps_in_venv
  run_tests
  start_server
else
  install_deps_system
  run_tests
  start_server
fi