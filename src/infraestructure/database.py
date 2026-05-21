# =============================================================================
# infraestructure/database.py  —  CAPA DE INFRAESTRUCTURA: CONEXIÓN A BD
# =============================================================================
# Este archivo es responsable de establecer la conexión con la base de datos
# MySQL usando SQLAlchemy como ORM (Object-Relational Mapper).
#
# ¿Qué es un ORM?
#   Un ORM traduce objetos Python a filas de base de datos y viceversa.
#   En lugar de escribir SQL puro, trabajamos con clases y objetos Python.
#
# Flujo de conexión:
#   .env → load_dotenv() → DATABASE_URL → engine → SessionLocal → get_db()
#
# Conceptos clave:
#   - Engine:       representa la conexión física al motor de base de datos
#   - Session:      unidad de trabajo que acumula operaciones antes de enviarlas a la BD
#   - Base:         clase padre de la que heredan todos los modelos ORM
# =============================================================================

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Carga las variables definidas en el archivo .env al entorno del proceso.
# Esto permite leer DB_HOST, DB_USER, etc. sin escribirlos directamente en el código.
load_dotenv()

# ----------------------------------------------------------------------------
# Construcción de la URL de conexión
# Formato: dialecto+driver://usuario:contraseña@host:puerto/nombre_bd
#   - mysql+pymysql indica que usamos MySQL con el driver PyMySQL
#   - os.getenv() lee cada variable del archivo .env
# ----------------------------------------------------------------------------
DATABASE_URL = (
    f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME')}"
)

# ----------------------------------------------------------------------------
# Engine: el motor de conexión. Es el objeto de más bajo nivel.
#   pool_pre_ping=True: antes de usar una conexión del pool, verifica que
#   siga activa. Evita errores por conexiones caídas (p.ej. por timeout en AWS).
# ----------------------------------------------------------------------------
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# ----------------------------------------------------------------------------
# SessionLocal: fábrica de sesiones.
#   - autocommit=False: los cambios NO se guardan solos; hay que llamar commit()
#   - autoflush=False:  los cambios no se envían a la BD hasta hacer commit()
# Cada petición HTTP obtendrá su propia sesión independiente.
# ----------------------------------------------------------------------------
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ----------------------------------------------------------------------------
# Base: clase declarativa de la que heredan todos los modelos ORM.
# Al heredar de Base, SQLAlchemy sabe que esa clase representa una tabla.
# ----------------------------------------------------------------------------
class Base(DeclarativeBase):
    pass


# ----------------------------------------------------------------------------
# get_db: generador que provee una sesión de BD a cada endpoint de FastAPI.
#
# FastAPI llama a esta función automáticamente gracias a Depends(get_db).
# El bloque try/finally garantiza que la sesión se cierre siempre,
# incluso si ocurre una excepción durante la petición.
#
# Uso en un endpoint:
#   def mi_endpoint(db: Session = Depends(get_db)):
#       ...
# ----------------------------------------------------------------------------
def get_db():
    db = SessionLocal()   # Abre una sesión nueva
    try:
        yield db          # Entrega la sesión al endpoint que la solicitó
    finally:
        db.close()        # Cierra la sesión al terminar la petición


