#el archivo main es el archivo pricipal de nuestra App

# Para arrancar el servidor ejecutar en la terminal:
#   venv\Scripts\uvicorn.exe main:app --reload
#
# La documentación interactiva estará disponible en:
#   http://localhost:8000/docs   ← Swagger UI (recomendado para probar)
#   http://localhost:8000/redoc  ← ReDoc (documentación alternativa)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.route import router

#Cracion del aplicacion en FastApi
#definimos el titulo, descripcion y una version

app = FastAPI(
    title="IUTEDE Gestion de Recursos TICS",
    description="Api curso modelado de sistemas",
    version="1.0.0"
)
#actualizamos el cros
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Acepta peticiones desde cualquier origen
    allow_methods=["*"],   # Permite todos los métodos HTTP (GET, POST, PUT, etc.)
    allow_headers=["*"],   # Permite todos los headers
)

# registrar las rutas definidas en el archivo route.py 
app.include_router(router)

#crear un endpoint para validar la salud del API
@app.get("/",tags=["Health salud"])
def healht_check():
    return {"Status":"ok", "api":"IUTEDE Backend", "version":"1.0.0" }
