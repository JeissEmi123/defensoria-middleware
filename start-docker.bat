@echo off
echo ========================================
echo Verificando Docker y levantando servicios
echo ========================================

echo.
echo Verificando Docker Desktop...
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker no está instalado o Docker Desktop no está iniciado.
    echo Por favor, inicia Docker Desktop e intenta de nuevo.
    exit /b 1
)

echo Docker está disponible.
echo.

echo Levantando contenedores...
docker-compose up -d

echo.
echo Esperando a que la base de datos esté lista...
timeout /t 10 /nobreak >nul

echo.
echo Verificando estado de contenedores...
docker-compose ps

echo.
echo ========================================
echo Servicios listos!
echo ========================================
