
# =============================================================================
# infraestructure/repository.py  —  CAPA DE INFRAESTRUCTURA: REPOSITORIOS
# =============================================================================
# Un repositorio encapsula toda la lógica de acceso a datos (las consultas SQL).
# Su misión es aislar a las demás capas de los detalles de cómo se lee y
# escribe en la base de datos.
#
# Patrón usado: Repository Pattern
#   - BaseRepository:  clase genérica con las operaciones CRUD comunes a todas
#                      las entidades (listar, buscar, crear, actualizar, borrar)
#   - Repositorios específicos: heredan de Base y añaden consultas propias
#     de cada entidad (buscar por correo, por matrícula, filtrar por estado, etc.)
#
# ¿Por qué separar repositorios de servicios?
#   - El repositorio solo sabe "cómo guardar/recuperar datos"
#   - El servicio sabe "qué hacer con esos datos" (lógica de negocio)
#   - Si mañana cambiamos MySQL por PostgreSQL, solo tocamos esta capa.
# =============================================================================

from typing import Optional, List, Type, TypeVar
from sqlalchemy.orm import Session
from src.domain.models import (
    Rol, Usuario, Estudiante, Profesor, Monitor,
    Recurso, EquipoPortatil, Laboratorio,
    Reserva, Prestamo, Novedad, Sancion,
)

# TypeVar se usa para que el tipo de retorno de los métodos genéricos
# sea consistente con el modelo que se está usando (Rol, Usuario, etc.)
T = TypeVar("T")


# =============================================================================
# BASE REPOSITORY  —  Operaciones CRUD genéricas
# Al heredar de esta clase, cada repositorio específico obtiene gratis
# los métodos get_all, get_by_id, create, update y delete.
# =============================================================================
class BaseRepository:
    #Define el constructor de BaseRepository — se ejecuta automáticamente al crear una instancia.
    def __init__(self, model: Type, db: Session):
        # Session es el tipo de SQLAlchemy que maneja transacciones
        # model: la clase ORM que este repositorio gestiona (Rol, Usuario, etc.)
        # db:    la sesión de base de datos inyectada desde el endpoint
        self.model = model
        self.db = db

    def get_all(self, skip: int = 0, limit: int = 100) -> List:
        # offset(skip): salta los primeros N registros → útil para paginación
        # limit(limit): devuelve como máximo N registros → evita traer miles de filas
        # Le dice a SQLAlchemy qué tabla consultar — equivale a SELECT * FROM tabla.
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def get_by_id(self, record_id: int) -> Optional: # si no encuentra nada retorna none
        # __mapper__.primary_key[0].name obtiene dinámicamente el nombre de la PK
        # de cualquier modelo (id_rol, id_usuario, id_recurso, etc.)
        # getattr() accede al atributo por nombre → equivale a Model.id_xxx
        # Obtiene dinámicamente el nombre de la columna PK de cualquier modelo:
        pk = self.model.__mapper__.primary_key[0].name
        return self.db.query(self.model).filter(
            getattr(self.model, pk) == record_id
        ).first()

    def create(self, obj) -> object:
        # Si algo falla aquí, la transacción se revierte y no se guarda nada.

        self.db.add(obj)        # Añade el objeto a la sesión (aún no en la BD)
        self.db.commit()        # Envía el INSERT a la BD y confirma la transacción
        self.db.refresh(obj)    # Recarga el objeto desde la BD (obtiene el ID generado)
        return obj

    def update(self, obj) -> object: #indica que devuelve el objeto actualizado y recargado desde la BD:
        # El objeto ya está en la sesión con los cambios aplicados.
        # Solo hace falta commit() para persistirlos.
        self.db.commit()
        self.db.refresh(obj)    # Recarga para reflejar los valores actualizados
        return obj

    def delete(self, record_id: int) -> bool:
        obj = self.get_by_id(record_id)
        if not obj:
            return False        # Retorna False si el registro no existe
        self.db.delete(obj)
        self.db.commit()
        return True             # Retorna True si se eliminó correctamente


# =============================================================================
# REPOSITORIOS ESPECÍFICOS
# Heredan de BaseRepository y añaden consultas propias de cada entidad.
# =============================================================================

class RolRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(Rol, db)   # Indica a BaseRepository que trabaja con Rol

    def get_by_nombre(self, nombre: str) -> Optional[Rol]:
        # filter() genera un WHERE en el SQL: WHERE nombre_rol = :nombre
        return self.db.query(Rol).filter(Rol.nombre_rol == nombre).first()


class UsuarioRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(Usuario, db)

    def get_by_correo(self, correo: str) -> Optional[Usuario]:
        # Útil para verificar si un correo ya está registrado o para el login
        return self.db.query(Usuario).filter(Usuario.correo == correo).first()


class EstudianteRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(Estudiante, db)

    def get_by_matricula(self, matricula: str) -> Optional[Estudiante]:
        return self.db.query(Estudiante).filter(Estudiante.matricula == matricula).first()


class ProfesorRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(Profesor, db)
        # No necesita consultas adicionales; las de BaseRepository son suficientes


class MonitorRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(Monitor, db)

    def get_by_turno(self, id_turno: int) -> List[Monitor]:
        # Devuelve TODOS los monitores de un turno → .all() en lugar de .first()
        return self.db.query(Monitor).filter(Monitor.id_turno == id_turno).all()


class RecursoRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(Recurso, db)

    def get_by_placa(self, id_placa: str) -> Optional[Recurso]:
        return self.db.query(Recurso).filter(Recurso.id_placa == id_placa).first()

    def get_by_tipo(self, tipo: str) -> List[Recurso]:
        # Permite filtrar solo portátiles o solo laboratorios
        return self.db.query(Recurso).filter(Recurso.tipo_recurso == tipo).all()

    def get_disponibles(self) -> List[Recurso]:
        # Filtra solo los recursos cuyo estado es exactamente "Disponible"
        return self.db.query(Recurso).filter(Recurso.estado == "Disponible").all()


class EquipoPortatilRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(EquipoPortatil, db)


class LaboratorioRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(Laboratorio, db)


class ReservaRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(Reserva, db)

    def get_by_usuario(self, id_usuario: int) -> List[Reserva]:
        # Historial de todas las reservas hechas por un usuario específico
        return self.db.query(Reserva).filter(Reserva.id_usuario_solicita == id_usuario).all()

    def get_by_recurso(self, id_recurso: int) -> List[Reserva]:
        # Todas las reservas sobre un recurso (útil para ver disponibilidad)
        return self.db.query(Reserva).filter(Reserva.id_recurso == id_recurso).all()

    def get_pendientes(self) -> List[Reserva]:
        # Las que aún no han sido revisadas por un monitor
        return self.db.query(Reserva).filter(Reserva.estado == "Pendiente").all()


class PrestamoRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(Prestamo, db)

    def get_by_reserva(self, id_reserva: int) -> Optional[Prestamo]:
        return self.db.query(Prestamo).filter(Prestamo.id_reserva == id_reserva).first()

    def get_activos(self) -> List[Prestamo]:
        # Un préstamo está activo si hora_devolucion es NULL (no se ha devuelto aún)
        # noqa: E711 suprime la advertencia del linter; SQLAlchemy requiere == None aquí
        return self.db.query(Prestamo).filter(Prestamo.hora_devolucion == None).all()  # noqa: E711


class NovedadRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(Novedad, db)

    def get_by_recurso(self, id_recurso: int) -> List[Novedad]:
        # Historial de incidentes de un recurso específico
        return self.db.query(Novedad).filter(Novedad.id_recurso == id_recurso).all()

    def get_by_estado(self, estado: str) -> List[Novedad]:
        # Filtra por estado: "Reportada", "En revisión", "Resuelta"
        return self.db.query(Novedad).filter(Novedad.estado == estado).all()


class SancionRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(Sancion, db)

    def get_by_estudiante(self, id_usuario: int) -> List[Sancion]:
        # Todo el historial de sanciones de un estudiante
        return self.db.query(Sancion).filter(Sancion.id_usuario_estudiante == id_usuario).all()

    def get_activas_por_estudiante(self, id_usuario: int) -> List[Sancion]:
        # Solo las sanciones vigentes → permite saber si un estudiante puede pedir prestado
        # filter() acepta múltiples condiciones separadas por comas (equivale a AND)
        return self.db.query(Sancion).filter(
            Sancion.id_usuario_estudiante == id_usuario,
            Sancion.estado == "Activa",
        ).all()

    
