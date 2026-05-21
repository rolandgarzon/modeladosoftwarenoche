#este archivo nos permite probar la conexion a la DB
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))
from sqlalchemy import text
from infraestructure.database import engine, SessionLocal, DATABASE_URL

def test_connection():
    print(f"Intentando conectar a l abase de datos: {DATABASE_URL}")

    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM ROLES"))
            print(" Engine Conectado correctamente")
            print(f"Resultado select : {result.fetchone()}")
    except Exception as e:
        print(f" Error en el engine: {e}")
        return
    print("La base de datos esta Operativa")

test_connection()

