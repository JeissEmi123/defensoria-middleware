#!/bin/bash

# Script de inicio para el middleware

echo "Esperando a que PostgreSQL esté listo..."
sleep 5

echo "Ejecutando migraciones de Alembic..."
alembic upgrade head

echo "Iniciando servidor FastAPI..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
