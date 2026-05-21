# =============================================================================
# main.py  —  PUNTO DE ENTRADA DE LA APLICACIÓN
# =============================================================================
# Este es el primer archivo que se ejecuta cuando se inicia el servidor.
# Aquí se crea la instancia de FastAPI, se configuran los middlewares
# (capas intermedias que procesan todas las peticiones) y se registran
# las rutas definidas en la capa API.
#
# Para arrancar el servidor ejecutar en la terminal:
#   venv\Scripts\uvicorn.exe main:app --reload
#
# La documentación interactiva estará disponible en:
#   http://localhost:8000/docs   ← Swagger UI (recomendado para probar)
#   http://localhost:8000/redoc  ← ReDoc (documentación alternativa)
# =============================================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importamos el router que agrupa todos los endpoints definidos en route.py
from src.api.route import router

# ----------------------------------------------------------------------------
# Creación de la aplicación FastAPI
# Los parámetros title, description y version aparecen en /docs
# ----------------------------------------------------------------------------
app = FastAPI(
    title="UTEDE - Gestión de Laboratorios",
    description="API para la gestión de recursos, reservas y préstamos de equipos y laboratorios universitarios.",
    version="1.0.0",
)

# ----------------------------------------------------------------------------
# Middleware de CORS (Cross-Origin Resource Sharing)
# Permite que el frontend (React en otro puerto) pueda hacer peticiones a esta API.
# En producción se debe cambiar allow_origins=["*"] por la URL exacta del frontend,
# por ejemplo: allow_origins=["http://localhost:5173"]
# ----------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # Acepta peticiones desde cualquier origen
    allow_credentials=True,     # Permite enviar cookies y headers de autenticación
    allow_methods=["*"],        # Permite todos los métodos HTTP (GET, POST, PUT, etc.)
    allow_headers=["*"],        # Permite todos los headers
)

# Registramos todas las rutas definidas en route.py bajo el prefijo /api/v1
app.include_router(router)


# ----------------------------------------------------------------------------
# Endpoint de salud (health check)
# Sirve para verificar rápidamente que el servidor está en línea.
# GET http://localhost:8000/
# ----------------------------------------------------------------------------
@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "api": "UTEDE Backend", "version": "1.0.0"}
