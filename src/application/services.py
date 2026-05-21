# =============================================================================
# application/services.py  —  CAPA DE APLICACIÓN: SERVICIOS (CASOS DE USO)
# =============================================================================
# Los servicios contienen la lógica de negocio del sistema.
# Son el "cerebro" de la aplicación: saben QUÉ hacer, pero delegan a los
# repositorios el CÓMO guardar o recuperar datos.
#
# Responsabilidades de esta capa:
#   - Orquestar llamadas a uno o varios repositorios
#   - Aplicar reglas de negocio (ej: una reserva solo se puede aprobar si
#     está en estado "Pendiente")
#   - Transformar datos antes de devolverlos a la capa API
#
# Separación de responsabilidades:
#   Capa API   →  recibe la petición HTTP, valida el formato (Pydantic)
#   Servicio   →  aplica la lógica de negocio
#   Repositorio →  ejecuta la consulta SQL
#
# Cada servicio recibe la sesión de BD (db) en su constructor y crea
# internamente el repositorio que necesita. Así la capa API no sabe nada
# de SQLAlchemy ni de SQL.
# =============================================================================

from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from src.domain.models import (
    Rol, Usuario, Estudiante, Profesor, Monitor,
    Recurso, EquipoPortatil, Laboratorio,
    Reserva, Prestamo, Novedad, Sancion,
)
from src.infraestructure.repository import (
    RolRepository, UsuarioRepository, EstudianteRepository,
    ProfesorRepository, MonitorRepository, RecursoRepository,
    EquipoPortatilRepository, LaboratorioRepository,
    ReservaRepository, PrestamoRepository, NovedadRepository,
    SancionRepository,
)


# =============================================================================
# ROL SERVICE
# =============================================================================
class RolService:
    def __init__(self, db: Session):
        # Instancia el repositorio pasándole la sesión de BD
        self.repo = RolRepository(db)

    def listar(self) -> List[Rol]:
        return self.repo.get_all()

    def obtener(self, id_rol: int) -> Optional[Rol]:
        return self.repo.get_by_id(id_rol)

    def crear(self, nombre_rol: str) -> Rol: # 1. Crea el objeto en memoria
        # Construye el objeto de dominio y lo pasa al repositorio para persistirlo
        return self.repo.create(Rol(nombre_rol=nombre_rol)) # 2. Lo persiste en la BD

    def eliminar(self, id_rol: int) -> bool:
        return self.repo.delete(id_rol)


# =============================================================================
# USUARIO SERVICE
# =============================================================================
class UsuarioService:
    def __init__(self, db: Session):
        self.repo = UsuarioRepository(db)

    def listar(self) -> List[Usuario]:
        return self.repo.get_all()

    def obtener(self, id_usuario: int) -> Optional[Usuario]:
        return self.repo.get_by_id(id_usuario)

    def obtener_por_correo(self, correo: str) -> Optional[Usuario]:
        # Útil para login: busca el usuario por correo para verificar contraseña
        return self.repo.get_by_correo(correo)

    def crear(self, id_rol: int, nombre_completo: str, correo: str, contrasena_hash: str) -> Usuario:
        # NOTA: la contraseña debe llegar ya hasheada desde el cliente o desde
        # un endpoint de registro. Nunca hashear aquí, para que sea responsabilidad
        # explícita del llamador.
        usuario = Usuario(
            id_rol=id_rol,
            nombre_completo=nombre_completo,
            correo=correo,
            contrasena_hash=contrasena_hash
        )
        return self.repo.create(usuario)

    def actualizar(self, id_usuario: int, **kwargs) -> Optional[Usuario]:
        # **kwargs recibe campos dinámicos: solo actualiza los campos enviados
        # exclude_none=True en el schema garantiza que los campos vacíos no lleguen aquí
        usuario = self.repo.get_by_id(id_usuario)
        if not usuario:
            return None         # El servicio devuelve None; el endpoint lanza el 404
        for key, value in kwargs.items():
            if hasattr(usuario, key) and value is not None:
                setattr(usuario, key, value)    # Modifica solo los campos recibidos
        return self.repo.update(usuario)

    def eliminar(self, id_usuario: int) -> bool:
        return self.repo.delete(id_usuario)


# =============================================================================
# ESTUDIANTE SERVICE
# =============================================================================
class EstudianteService:
    def __init__(self, db: Session):
        self.repo = EstudianteRepository(db)

    def listar(self) -> List[Estudiante]:
        return self.repo.get_all()

    def obtener(self, id_usuario: int) -> Optional[Estudiante]:
        return self.repo.get_by_id(id_usuario)

    def crear(self, id_usuario: int, matricula: str, programa: str) -> Estudiante:
        # Primero debe existir el Usuario base; este método solo agrega el perfil estudiante
        return self.repo.create(Estudiante(id_usuario=id_usuario, matricula=matricula, programa=programa))


# =============================================================================
# PROFESOR SERVICE
# =============================================================================
class ProfesorService:
    def __init__(self, db: Session):
        self.repo = ProfesorRepository(db)

    def listar(self) -> List[Profesor]:
        return self.repo.get_all()

    def obtener(self, id_usuario: int) -> Optional[Profesor]:
        return self.repo.get_by_id(id_usuario)

    def crear(self, id_usuario: int, departamento: str) -> Profesor:
        return self.repo.create(Profesor(id_usuario=id_usuario, departamento=departamento))


# =============================================================================
# MONITOR SERVICE
# =============================================================================
class MonitorService:
    def __init__(self, db: Session):
        self.repo = MonitorRepository(db)

    def listar(self) -> List[Monitor]:
        return self.repo.get_all()

    def obtener(self, id_usuario: int) -> Optional[Monitor]:
        return self.repo.get_by_id(id_usuario)

    def crear(self, id_usuario: int, id_turno: int) -> Monitor:
        return self.repo.create(Monitor(id_usuario=id_usuario, id_turno=id_turno))


# =============================================================================
# RECURSO SERVICE
# =============================================================================
class RecursoService:
    def __init__(self, db: Session):
        self.repo = RecursoRepository(db)

    def listar(self) -> List[Recurso]:
        return self.repo.get_all()

    def obtener(self, id_recurso: int) -> Optional[Recurso]:
        return self.repo.get_by_id(id_recurso)

    def listar_disponibles(self) -> List[Recurso]:
        # Delega al repositorio la consulta filtrada por estado
        return self.repo.get_disponibles()

    def listar_por_tipo(self, tipo: str) -> List[Recurso]:
        return self.repo.get_by_tipo(tipo)

    def crear(self, id_placa: str, marca: str, estado: str, tipo_recurso: str) -> Recurso:
        recurso = Recurso(id_placa=id_placa, marca=marca, estado=estado, tipo_recurso=tipo_recurso)
        return self.repo.create(recurso)

    def actualizar_estado(self, id_recurso: int, estado: str) -> Optional[Recurso]:
        # Caso de uso específico: cambiar solo el estado de un recurso
        # (sin necesidad de enviar todos sus campos)
        recurso = self.repo.get_by_id(id_recurso)
        if not recurso:
            return None
        recurso.estado = estado
        return self.repo.update(recurso)

    def eliminar(self, id_recurso: int) -> bool:
        return self.repo.delete(id_recurso)


# =============================================================================
# EQUIPO PORTÁTIL SERVICE
# =============================================================================
class EquipoPortatilService:
    def __init__(self, db: Session):
        self.repo = EquipoPortatilRepository(db)

    def listar(self) -> List[EquipoPortatil]:
        return self.repo.get_all()

    def obtener(self, id_recurso: int) -> Optional[EquipoPortatil]:
        return self.repo.get_by_id(id_recurso)

    def crear(self, id_recurso: int, modelo: str, sistema_operativo: str) -> EquipoPortatil:
        # id_recurso debe existir previamente en RECURSOS
        return self.repo.create(EquipoPortatil(id_recurso=id_recurso, modelo=modelo, sistema_operativo=sistema_operativo))


# =============================================================================
# LABORATORIO SERVICE
# =============================================================================
class LaboratorioService:
    def __init__(self, db: Session):
        self.repo = LaboratorioRepository(db)

    def listar(self) -> List[Laboratorio]:
        return self.repo.get_all()

    def obtener(self, id_recurso: int) -> Optional[Laboratorio]:
        return self.repo.get_by_id(id_recurso)

    def crear(self, id_recurso: int, capacidad: int, ubicacion: str, software: Optional[str] = None) -> Laboratorio:
        return self.repo.create(
            Laboratorio(id_recurso=id_recurso, capacidad=capacidad, ubicacion=ubicacion, software=software)
        )


# =============================================================================
# RESERVA SERVICE
# Aquí está la lógica del flujo de aprobación de reservas.
# =============================================================================
class ReservaService:
    def __init__(self, db: Session):
        self.repo = ReservaRepository(db)

    def listar(self) -> List[Reserva]:
        return self.repo.get_all()

    def obtener(self, id_reserva: int) -> Optional[Reserva]:
        return self.repo.get_by_id(id_reserva)

    def listar_por_usuario(self, id_usuario: int) -> List[Reserva]:
        return self.repo.get_by_usuario(id_usuario)

    def listar_pendientes(self) -> List[Reserva]:
        # Permite a los monitores ver qué reservas necesitan ser revisadas
        return self.repo.get_pendientes()

    def crear(
        self, id_usuario_solicita: int, id_recurso: int,
        fecha_inicio: datetime, fecha_fin: datetime, proposito: str,
    ) -> Reserva:
        # Al crearse, el estado siempre es "Pendiente"
        reserva = Reserva(
            id_usuario_solicita=id_usuario_solicita,
            id_recurso=id_recurso,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            proposito=proposito,
            estado="Pendiente",
        )
        return self.repo.create(reserva)

    def aprobar(self, id_reserva: int, id_monitor: int) -> Optional[Reserva]:
        # Regla de negocio: cambia el estado a "Aprobada" y registra qué monitor aprobó
        reserva = self.repo.get_by_id(id_reserva)
        if not reserva:
            return None
        reserva.estado = "Aprobada"
        reserva.id_monitor_aprueba = id_monitor
        return self.repo.update(reserva)

    def rechazar(self, id_reserva: int) -> Optional[Reserva]:
        reserva = self.repo.get_by_id(id_reserva)
        if not reserva:
            return None
        reserva.estado = "Rechazada"
        return self.repo.update(reserva)

    def cancelar(self, id_reserva: int) -> Optional[Reserva]:
        # El propio usuario puede cancelar su reserva antes de que sea procesada
        reserva = self.repo.get_by_id(id_reserva)
        if not reserva:
            return None
        reserva.estado = "Cancelada"
        return self.repo.update(reserva)


# =============================================================================
# PRÉSTAMO SERVICE
# Gestiona la entrega y devolución física de recursos.
# =============================================================================
class PrestamoService:
    def __init__(self, db: Session):
        self.repo = PrestamoRepository(db)

    def listar(self) -> List[Prestamo]:
        return self.repo.get_all()

    def obtener(self, id_prestamo: int) -> Optional[Prestamo]:
        return self.repo.get_by_id(id_prestamo)

    def listar_activos(self) -> List[Prestamo]:
        # Préstamos sin devolución registrada = recursos que están fuera del laboratorio
        return self.repo.get_activos()

    def crear(self, id_reserva: int, id_monitor_entrega: int) -> Prestamo:
        # Se llama cuando el monitor entrega físicamente el recurso.
        # datetime.now() registra el momento exacto de la entrega.
        prestamo = Prestamo(
            id_reserva=id_reserva,
            id_monitor_entrega=id_monitor_entrega,
            hora_entrega=datetime.now(),
        )
        return self.repo.create(prestamo)

    def registrar_devolucion(self, id_prestamo: int, estado_recepcion: str) -> Optional[Prestamo]:
        # Se llama cuando el estudiante devuelve el recurso.
        # El monitor registra en qué condición lo recibe (Bueno, Con daños, etc.)
        prestamo = self.repo.get_by_id(id_prestamo)
        if not prestamo:
            return None
        prestamo.hora_devolucion = datetime.now()
        prestamo.estado_recepcion = estado_recepcion
        return self.repo.update(prestamo)


# =============================================================================
# NOVEDAD SERVICE
# Gestión de incidentes y daños reportados.
# =============================================================================
class NovedadService:
    def __init__(self, db: Session):
        self.repo = NovedadRepository(db)

    def listar(self) -> List[Novedad]:
        return self.repo.get_all()

    def obtener(self, id_novedad: int) -> Optional[Novedad]:
        return self.repo.get_by_id(id_novedad)

    def listar_por_recurso(self, id_recurso: int) -> List[Novedad]:
        # Permite ver el historial de problemas de un equipo o laboratorio
        return self.repo.get_by_recurso(id_recurso)

    def crear(
        self, id_recurso: int, id_usuario_reporta: int,
        descripcion: str, gravedad: str, id_prestamo: Optional[int] = None,
    ) -> Novedad:
        # La fecha del reporte se establece automáticamente al momento de creación
        novedad = Novedad(
            id_recurso=id_recurso,
            id_usuario_reporta=id_usuario_reporta,
            id_prestamo=id_prestamo,    # Puede ser None si no está ligada a un préstamo
            fecha_reporte=datetime.now(),
            descripcion=descripcion,
            gravedad=gravedad,
            estado="Reportada",
        )
        return self.repo.create(novedad)

    def cambiar_estado(self, id_novedad: int, estado: str) -> Optional[Novedad]:
        # Permite avanzar la novedad por su ciclo: Reportada → En revisión → Resuelta
        novedad = self.repo.get_by_id(id_novedad)
        if not novedad:
            return None
        novedad.estado = estado
        return self.repo.update(novedad)


# =============================================================================
# SANCIÓN SERVICE
# Gestión de restricciones aplicadas a estudiantes.
# =============================================================================
class SancionService:
    def __init__(self, db: Session):
        self.repo = SancionRepository(db)

    def listar(self) -> List[Sancion]:
        return self.repo.get_all()

    def obtener(self, id_sancion: int) -> Optional[Sancion]:
        return self.repo.get_by_id(id_sancion)

    def listar_por_estudiante(self, id_usuario: int) -> List[Sancion]:
        # Historial completo de sanciones de un estudiante
        return self.repo.get_by_estudiante(id_usuario)

    def crear(
        self, id_usuario_estudiante: int, id_prestamo: int,
        fecha_inicio: datetime, fecha_fin: datetime, motivo: str,
    ) -> Sancion:
        # El estado inicial siempre es "Activa"
        sancion = Sancion(
            id_usuario_estudiante=id_usuario_estudiante,
            id_prestamo=id_prestamo,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            motivo=motivo,
            estado="Activa",
        )
        return self.repo.create(sancion)

    def levantar(self, id_sancion: int) -> Optional[Sancion]:
        # Un administrador puede levantar (cancelar) una sanción antes de que venza
        sancion = self.repo.get_by_id(id_sancion)
        if not sancion:
            return None
        sancion.estado = "Levantada"
        return self.repo.update(sancion)
