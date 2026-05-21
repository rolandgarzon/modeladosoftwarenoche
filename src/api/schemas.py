# =============================================================================
# api/schemas.py  —  CAPA API: SCHEMAS PYDANTIC (DTOs)
# =============================================================================
# Los schemas son los "contratos" de la API: definen exactamente qué datos
# se esperan en cada petición y qué datos se devuelven en cada respuesta.
#
# DTO = Data Transfer Object (Objeto de Transferencia de Datos)
# Su función es separar la representación de red (JSON) de los modelos de BD.
#
# Convención de nombres usada en este proyecto:
#   XxxCreate   → datos que llegan en el BODY al crear un recurso (POST)
#   XxxUpdate   → datos para actualizar (PUT/PATCH); todos los campos son opcionales
#   XxxAprobar  → datos para una acción específica de negocio (PATCH)
#   XxxResponse → datos que se devuelven al cliente en la respuesta (GET/POST/PUT)
#
# ¿Por qué no usar los modelos ORM directamente?
#   - Los modelos tienen campos sensibles (contrasena_hash) que no deben exponerse
#   - Los modelos tienen relaciones circulares que no se pueden serializar a JSON
#   - Los DTOs permiten versionar la API sin cambiar el modelo de BD
#
# model_config = {"from_attributes": True}
#   Le dice a Pydantic que puede construir el schema leyendo atributos de un
#   objeto Python (como un modelo SQLAlchemy), no solo desde un diccionario.
#   Esto es lo que hace posible: return UsuarioResponse.model_validate(usuario_orm)
# =============================================================================

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


# =============================================================================
# ROL
# =============================================================================
class RolCreate(BaseModel):
    # Solo se envía el nombre; el ID lo asigna la BD automáticamente
    nombre_rol: str

class RolResponse(BaseModel):
    id_rol: int
    nombre_rol: str
    model_config = {"from_attributes": True}


# =============================================================================
# USUARIO
# Nota: la contraseña se recibe en Create pero nunca se devuelve en Response.
# Ese es uno de los valores principales del patrón DTO.
# =============================================================================
class UsuarioCreate(BaseModel):
    id_rol: int
    nombre_completo: str
    correo: str
    contrasena_hash: str    # En producción esto llegaría ya hasheado

class UsuarioUpdate(BaseModel):
    # Optional con valor None indica que el campo es opcional en la petición.
    # Solo se actualizan los campos que el cliente envíe (los demás quedan igual).
    nombre_completo: Optional[str] = None
    correo: Optional[str] = None
    id_rol: Optional[int] = None

class UsuarioResponse(BaseModel):
    id_usuario: int
    id_rol: int
    nombre_completo: str
    correo: str
    # contrasena_hash NO aparece aquí → nunca se expone al cliente
    model_config = {"from_attributes": True}


# =============================================================================
# ESTUDIANTE
# =============================================================================
class EstudianteCreate(BaseModel):
    id_usuario: int     # El usuario base debe crearse primero
    matricula: str
    programa: str

class EstudianteResponse(BaseModel):
    id_usuario: int
    matricula: str
    programa: str
    model_config = {"from_attributes": True}


# =============================================================================
# PROFESOR
# =============================================================================
class ProfesorCreate(BaseModel):
    id_usuario: int
    departamento: str

class ProfesorResponse(BaseModel):
    id_usuario: int
    departamento: str
    model_config = {"from_attributes": True}


# =============================================================================
# MONITOR
# =============================================================================
class MonitorCreate(BaseModel):
    id_usuario: int
    id_turno: int

class MonitorResponse(BaseModel):
    id_usuario: int
    id_turno: int
    model_config = {"from_attributes": True}


# =============================================================================
# RECURSO
# =============================================================================
class RecursoCreate(BaseModel):
    id_placa: str
    marca: str
    estado: str         # Valores esperados: "Disponible", "En mantenimiento", etc.
    tipo_recurso: str   # Valores esperados: "Portatil", "Laboratorio"

class RecursoEstadoUpdate(BaseModel):
    # Schema especial para el endpoint PATCH /recursos/{id}/estado
    # Solo contiene el campo que se puede cambiar con ese endpoint
    estado: str

class RecursoResponse(BaseModel):
    id_recurso: int
    id_placa: str
    marca: str
    estado: str
    tipo_recurso: str
    model_config = {"from_attributes": True}


# =============================================================================
# EQUIPO PORTÁTIL
# =============================================================================
class EquipoPortatilCreate(BaseModel):
    id_recurso: int     # El recurso base debe crearse primero
    modelo: str
    sistema_operativo: str

class EquipoPortatilResponse(BaseModel):
    id_recurso: int
    modelo: str
    sistema_operativo: str
    model_config = {"from_attributes": True}


# =============================================================================
# LABORATORIO
# =============================================================================
class LaboratorioCreate(BaseModel):
    id_recurso: int
    capacidad: int
    ubicacion: str
    software: Optional[str] = None  # Campo opcional: no todos los labs tienen software especial

class LaboratorioResponse(BaseModel):
    id_recurso: int
    capacidad: int
    ubicacion: str
    software: Optional[str] = None
    model_config = {"from_attributes": True}


# =============================================================================
# RESERVA
# =============================================================================
class ReservaCreate(BaseModel):
    id_usuario_solicita: int
    id_recurso: int
    fecha_inicio: datetime  # Pydantic valida automáticamente el formato ISO 8601
    fecha_fin: datetime
    proposito: str

class ReservaAprobar(BaseModel):
    # Schema para el endpoint PATCH /reservas/{id}/aprobar
    # Solo necesita saber qué monitor está aprobando
    id_monitor_aprueba: int

class ReservaResponse(BaseModel):
    id_reserva: int
    id_usuario_solicita: int
    id_recurso: int
    id_monitor_aprueba: Optional[int] = None    # None hasta que sea aprobada
    fecha_inicio: datetime
    fecha_fin: datetime
    estado: str
    proposito: str
    model_config = {"from_attributes": True}


# =============================================================================
# PRÉSTAMO
# =============================================================================
class PrestamoCreate(BaseModel):
    id_reserva: int
    id_monitor_entrega: int
    # hora_entrega NO se envía: se registra automáticamente con datetime.now()

class PrestamoDevolucion(BaseModel):
    # Schema para el endpoint PATCH /prestamos/{id}/devolucion
    estado_recepcion: str   # Ej: "Bueno", "Con rayones", "Falta cargador"

class PrestamoResponse(BaseModel):
    id_prestamo: int
    id_reserva: int
    id_monitor_entrega: int
    hora_entrega: datetime
    hora_devolucion: Optional[datetime] = None  # None si el préstamo sigue activo
    estado_recepcion: Optional[str] = None
    model_config = {"from_attributes": True}


# =============================================================================
# NOVEDAD
# =============================================================================
class NovedadCreate(BaseModel):
    id_recurso: int
    id_usuario_reporta: int
    id_prestamo: Optional[int] = None   # Opcional: puede no estar ligada a un préstamo
    descripcion: str
    gravedad: str   # Valores esperados: "Leve", "Moderada", "Grave"

class NovedadEstado(BaseModel):
    # Schema para el endpoint PATCH /novedades/{id}/estado
    estado: str     # Valores esperados: "En revisión", "Resuelta"

class NovedadResponse(BaseModel):
    id_novedad: int
    id_recurso: int
    id_usuario_reporta: int
    id_prestamo: Optional[int] = None
    fecha_reporte: datetime
    descripcion: str
    gravedad: str
    estado: str
    model_config = {"from_attributes": True}


# =============================================================================
# SANCIÓN
# =============================================================================
class SancionCreate(BaseModel):
    id_usuario_estudiante: int
    id_prestamo: int
    fecha_inicio: datetime
    fecha_fin: datetime
    motivo: str

class SancionResponse(BaseModel):
    id_sancion: int
    id_usuario_estudiante: int
    id_prestamo: int
    fecha_inicio: datetime
    fecha_fin: datetime
    motivo: str
    estado: str     # "Activa" o "Levantada"
    model_config = {"from_attributes": True}
