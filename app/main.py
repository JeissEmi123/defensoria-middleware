from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware
try:
    from fastapi.responses import ORJSONResponse
    DEFAULT_RESPONSE_CLASS = ORJSONResponse
except ImportError:
    # Si orjson no está disponible, usar JSONResponse con charset UTF-8
    DEFAULT_RESPONSE_CLASS = JSONResponse
from app.config import get_settings
from app.api import auth, rbac, usuarios, password_reset, senales
from app.core.exceptions import DefensoriaException

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description='Sistema de autenticación Defensoría',
    redirect_slashes=False,  # Evitar redirecciones 307 que pierden headers
    default_response_class=DEFAULT_RESPONSE_CLASS  # UTF-8 por defecto
)

# CORS Configuration
# Orígenes permitidos: desarrollo local + producción GCP
ALLOWED_ORIGINS = [
    # Frontend en Cloud Run (Producción)
    "https://defensoria-frontend-411798681660.us-central1.run.app",
    
    # Desarrollo local - Todos los puertos comunes
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
    "http://localhost:3003",
    "http://localhost:3004",
    "http://localhost:3005",
    "http://localhost:3007",
    "http://localhost:5173",  # Vite default
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "http://127.0.0.1:3002",
    "http://127.0.0.1:3003",
    "http://127.0.0.1:3004",
    "http://127.0.0.1:3005",
    "http://127.0.0.1:3007",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8000",
    "http://192.168.78.247",
    "http://172.23.208.1:3003",
    "http://192.168.78.247:3004/",
    "http://172.23.208.1:3004/"
]

print(f"🔧 CORS Enabled for origins: {ALLOWED_ORIGINS}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if settings.app_env == "production" else ["*"],  # Permitir todos en desarrollo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Middleware para garantizar Content-Type con charset UTF-8
@app.middleware("http")
async def add_utf8_charset(request: Request, call_next):
    response = await call_next(request)
    if "application/json" in response.headers.get("content-type", ""):
        response.headers["content-type"] = "application/json; charset=utf-8"
    return response

# Manejador global de excepciones personalizadas
@app.exception_handler(DefensoriaException)
async def defensoria_exception_handler(request: Request, exc: DefensoriaException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.error_code,
            "message": exc.message,
            "details": exc.details
        },
        media_type="application/json; charset=utf-8"
    )

# Registrar routers
app.include_router(auth.router, prefix="/auth", tags=["Autenticación"])
app.include_router(rbac.router, prefix="/rbac", tags=["RBAC"])
app.include_router(usuarios.router, prefix="/usuarios", tags=["Usuarios"])
app.include_router(password_reset.router, prefix="/password", tags=["Recuperación de Contraseña"])
app.include_router(senales.router, prefix="/api/v1/senales", tags=["Señales"])

@app.get('/')
async def root():
    return {'message': 'Defensoria Middleware API', 'version': settings.app_version, 'status': 'operational'}

@app.get('/health')
async def health():
    return {'status': 'healthy'}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
