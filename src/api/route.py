# =============================================================================
# api/route.py  —  CAPA API: ENDPOINTS (RUTAS)
# =============================================================================
# Este archivo define todos los endpoints HTTP de la aplicación.
# Es la capa más externa: la primera que recibe las peticiones del cliente
# y la última en devolver la respuesta.
#
# Responsabilidades de esta capa:
#   1. Recibir la petición HTTP (método, URL, parámetros, body)
#   2. Validar el formato del body usando los schemas de Pydantic
#   3. Delegar la lógica al servicio correspondiente
#   4. Devolver la respuesta con el schema y código HTTP correcto
#
# Métodos HTTP usados y su significado:
#   GET    → Leer/consultar datos (sin efectos secundarios)
#   POST   → Crear un nuevo recurso
#   PUT    → Reemplazar un recurso completo
#   PATCH  → Modificar parcialmente un recurso o ejecutar una acción específica
#   DELETE → Eliminar un recurso
#
# Códigos de estado HTTP usados:
#   200 OK          → GET / PUT / PATCH exitosos (por defecto en FastAPI)
#   201 Created     → POST exitoso (recurso creado)
#   204 No Content  → DELETE exitoso (sin cuerpo en la respuesta)
#   404 Not Found   → El recurso solicitado no existe
#
# Depends(get_db):
#   FastAPI inyecta automáticamente una sesión de BD en cada endpoint.
#   El desarrollador no necesita abrir ni cerrar la sesión manualmente.
# =============================================================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

# get_db provee la sesión de BD a través del sistema de inyección de dependencias
from src.infraestructure.database import get_db

# Servicios: contienen la lógica de negocio
from src.application.services import (
    RolService, UsuarioService, EstudianteService, ProfesorService,
    MonitorService, RecursoService, EquipoPortatilService, LaboratorioService,
    ReservaService, PrestamoService, NovedadService, SancionService,
)

# Schemas: definen el contrato de entrada y salida de cada endpoint
from src.api.schemas import (
    RolCreate, RolResponse,
    UsuarioCreate, UsuarioUpdate, UsuarioResponse,
    EstudianteCreate, EstudianteResponse,
    ProfesorCreate, ProfesorResponse,
    MonitorCreate, MonitorResponse,
    RecursoCreate, RecursoEstadoUpdate, RecursoResponse,
    EquipoPortatilCreate, EquipoPortatilResponse,
    LaboratorioCreate, LaboratorioResponse,
    ReservaCreate, ReservaAprobar, ReservaResponse,
    PrestamoCreate, PrestamoDevolucion, PrestamoResponse,
    NovedadCreate, NovedadEstado, NovedadResponse,
    SancionCreate, SancionResponse,
)

# APIRouter agrupa las rutas; el prefix="/api/v1" se antepone a todas las URLs.
# El versionado /v1 permite en el futuro crear /v2 sin romper clientes existentes.
router = APIRouter(prefix="/api/v1")


# =============================================================================
# ROLES
# Endpoints: GET /api/v1/roles, GET /api/v1/roles/{id}, POST, DELETE
# =============================================================================

@router.get("/roles", response_model=List[RolResponse], tags=["Roles"])
def listar_roles(db: Session = Depends(get_db)):
    # Depends(get_db) le pide a FastAPI que ejecute get_db() e inyecte la sesión
    return RolService(db).listar()

@router.get("/roles/{id_rol}", response_model=RolResponse, tags=["Roles"])
def obtener_rol(id_rol: int, db: Session = Depends(get_db)):
    # {id_rol} en la URL es un path parameter; FastAPI lo convierte a int automáticamente
    rol = RolService(db).obtener(id_rol)
    if not rol:
        # HTTPException detiene la ejecución y devuelve la respuesta de error
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    return rol

@router.post("/roles", response_model=RolResponse, status_code=status.HTTP_201_CREATED, tags=["Roles"])
def crear_rol(data: RolCreate, db: Session = Depends(get_db)):
    # `data` es el body JSON validado automáticamente por Pydantic según RolCreate
    return RolService(db).crear(data.nombre_rol)

@router.delete("/roles/{id_rol}", status_code=status.HTTP_204_NO_CONTENT, tags=["Roles"])
def eliminar_rol(id_rol: int, db: Session = Depends(get_db)):
    if not RolService(db).eliminar(id_rol):
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    # Sin return: FastAPI devuelve 204 No Content automáticamente


# =============================================================================
# USUARIOS
# Endpoints: GET (lista), GET (uno), POST, PUT, DELETE
# =============================================================================

@router.get("/usuarios", response_model=List[UsuarioResponse], tags=["Usuarios"])
def listar_usuarios(db: Session = Depends(get_db)):
    return UsuarioService(db).listar()

@router.get("/usuarios/{id_usuario}", response_model=UsuarioResponse, tags=["Usuarios"])
def obtener_usuario(id_usuario: int, db: Session = Depends(get_db)):
    u = UsuarioService(db).obtener(id_usuario)
    if not u:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return u

@router.post("/usuarios", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED, tags=["Usuarios"])
def crear_usuario(data: UsuarioCreate, db: Session = Depends(get_db)):
    return UsuarioService(db).crear(data.id_rol, data.nombre_completo, data.correo, data.contrasena_hash)

@router.put("/usuarios/{id_usuario}", response_model=UsuarioResponse, tags=["Usuarios"])
def actualizar_usuario(id_usuario: int, data: UsuarioUpdate, db: Session = Depends(get_db)):
    # model_dump(exclude_none=True) convierte el schema a dict omitiendo los campos None
    # Así solo se actualizan los campos que el cliente envió
    u = UsuarioService(db).actualizar(id_usuario, **data.model_dump(exclude_none=True))
    if not u:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return u

@router.delete("/usuarios/{id_usuario}", status_code=status.HTTP_204_NO_CONTENT, tags=["Usuarios"])
def eliminar_usuario(id_usuario: int, db: Session = Depends(get_db)):
    if not UsuarioService(db).eliminar(id_usuario):
        raise HTTPException(status_code=404, detail="Usuario no encontrado")


# =============================================================================
# ESTUDIANTES
# =============================================================================

@router.get("/estudiantes", response_model=List[EstudianteResponse], tags=["Estudiantes"])
def listar_estudiantes(db: Session = Depends(get_db)):
    return EstudianteService(db).listar()

@router.get("/estudiantes/{id_usuario}", response_model=EstudianteResponse, tags=["Estudiantes"])
def obtener_estudiante(id_usuario: int, db: Session = Depends(get_db)):
    e = EstudianteService(db).obtener(id_usuario)
    if not e:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    return e

@router.post("/estudiantes", response_model=EstudianteResponse, status_code=status.HTTP_201_CREATED, tags=["Estudiantes"])
def crear_estudiante(data: EstudianteCreate, db: Session = Depends(get_db)):
    return EstudianteService(db).crear(data.id_usuario, data.matricula, data.programa)


# =============================================================================
# PROFESORES
# =============================================================================

@router.get("/profesores", response_model=List[ProfesorResponse], tags=["Profesores"])
def listar_profesores(db: Session = Depends(get_db)):
    return ProfesorService(db).listar()

@router.get("/profesores/{id_usuario}", response_model=ProfesorResponse, tags=["Profesores"])
def obtener_profesor(id_usuario: int, db: Session = Depends(get_db)):
    p = ProfesorService(db).obtener(id_usuario)
    if not p:
        raise HTTPException(status_code=404, detail="Profesor no encontrado")
    return p

@router.post("/profesores", response_model=ProfesorResponse, status_code=status.HTTP_201_CREATED, tags=["Profesores"])
def crear_profesor(data: ProfesorCreate, db: Session = Depends(get_db)):
    return ProfesorService(db).crear(data.id_usuario, data.departamento)


# =============================================================================
# MONITORES
# =============================================================================

@router.get("/monitores", response_model=List[MonitorResponse], tags=["Monitores"])
def listar_monitores(db: Session = Depends(get_db)):
    return MonitorService(db).listar()

@router.get("/monitores/{id_usuario}", response_model=MonitorResponse, tags=["Monitores"])
def obtener_monitor(id_usuario: int, db: Session = Depends(get_db)):
    m = MonitorService(db).obtener(id_usuario)
    if not m:
        raise HTTPException(status_code=404, detail="Monitor no encontrado")
    return m

@router.post("/monitores", response_model=MonitorResponse, status_code=status.HTTP_201_CREATED, tags=["Monitores"])
def crear_monitor(data: MonitorCreate, db: Session = Depends(get_db)):
    return MonitorService(db).crear(data.id_usuario, data.id_turno)


# =============================================================================
# RECURSOS
# Incluye el endpoint especial PATCH /recursos/{id}/estado
# que permite cambiar solo el estado sin enviar todos los campos.
# =============================================================================

@router.get("/recursos", response_model=List[RecursoResponse], tags=["Recursos"])
def listar_recursos(db: Session = Depends(get_db)):
    return RecursoService(db).listar()

@router.get("/recursos/disponibles", response_model=List[RecursoResponse], tags=["Recursos"])
def listar_disponibles(db: Session = Depends(get_db)):
    # Este endpoint debe estar ANTES de /recursos/{id_recurso}
    # porque FastAPI evalúa las rutas en orden: "disponibles" podría interpretarse
    # como un id_recurso de tipo string si el orden fuera incorrecto.
    return RecursoService(db).listar_disponibles()

@router.get("/recursos/{id_recurso}", response_model=RecursoResponse, tags=["Recursos"])
def obtener_recurso(id_recurso: int, db: Session = Depends(get_db)):
    r = RecursoService(db).obtener(id_recurso)
    if not r:
        raise HTTPException(status_code=404, detail="Recurso no encontrado")
    return r

@router.post("/recursos", response_model=RecursoResponse, status_code=status.HTTP_201_CREATED, tags=["Recursos"])
def crear_recurso(data: RecursoCreate, db: Session = Depends(get_db)):
    return RecursoService(db).crear(data.id_placa, data.marca, data.estado, data.tipo_recurso)

@router.patch("/recursos/{id_recurso}/estado", response_model=RecursoResponse, tags=["Recursos"])
def actualizar_estado_recurso(id_recurso: int, data: RecursoEstadoUpdate, db: Session = Depends(get_db)):
    # PATCH (no PUT) porque solo se modifica un campo, no el recurso completo
    r = RecursoService(db).actualizar_estado(id_recurso, data.estado)
    if not r:
        raise HTTPException(status_code=404, detail="Recurso no encontrado")
    return r

@router.delete("/recursos/{id_recurso}", status_code=status.HTTP_204_NO_CONTENT, tags=["Recursos"])
def eliminar_recurso(id_recurso: int, db: Session = Depends(get_db)):
    if not RecursoService(db).eliminar(id_recurso):
        raise HTTPException(status_code=404, detail="Recurso no encontrado")


# =============================================================================
# EQUIPOS PORTÁTILES
# =============================================================================

@router.get("/equipos-portatiles", response_model=List[EquipoPortatilResponse], tags=["Equipos Portátiles"])
def listar_equipos(db: Session = Depends(get_db)):
    return EquipoPortatilService(db).listar()

@router.get("/equipos-portatiles/{id_recurso}", response_model=EquipoPortatilResponse, tags=["Equipos Portátiles"])
def obtener_equipo(id_recurso: int, db: Session = Depends(get_db)):
    e = EquipoPortatilService(db).obtener(id_recurso)
    if not e:
        raise HTTPException(status_code=404, detail="Equipo portátil no encontrado")
    return e

@router.post("/equipos-portatiles", response_model=EquipoPortatilResponse, status_code=status.HTTP_201_CREATED, tags=["Equipos Portátiles"])
def crear_equipo(data: EquipoPortatilCreate, db: Session = Depends(get_db)):
    return EquipoPortatilService(db).crear(data.id_recurso, data.modelo, data.sistema_operativo)


# =============================================================================
# LABORATORIOS
# =============================================================================

@router.get("/laboratorios", response_model=List[LaboratorioResponse], tags=["Laboratorios"])
def listar_laboratorios(db: Session = Depends(get_db)):
    return LaboratorioService(db).listar()

@router.get("/laboratorios/{id_recurso}", response_model=LaboratorioResponse, tags=["Laboratorios"])
def obtener_laboratorio(id_recurso: int, db: Session = Depends(get_db)):
    lab = LaboratorioService(db).obtener(id_recurso)
    if not lab:
        raise HTTPException(status_code=404, detail="Laboratorio no encontrado")
    return lab

@router.post("/laboratorios", response_model=LaboratorioResponse, status_code=status.HTTP_201_CREATED, tags=["Laboratorios"])
def crear_laboratorio(data: LaboratorioCreate, db: Session = Depends(get_db)):
    return LaboratorioService(db).crear(data.id_recurso, data.capacidad, data.ubicacion, data.software)


# =============================================================================
# RESERVAS
# Incluye endpoints de acción: /aprobar, /rechazar, /cancelar
# =============================================================================

@router.get("/reservas", response_model=List[ReservaResponse], tags=["Reservas"])
def listar_reservas(db: Session = Depends(get_db)):
    return ReservaService(db).listar()

@router.get("/reservas/pendientes", response_model=List[ReservaResponse], tags=["Reservas"])
def listar_reservas_pendientes(db: Session = Depends(get_db)):
    # Las reservas pendientes son la bandeja de entrada del monitor
    return ReservaService(db).listar_pendientes()

@router.get("/reservas/usuario/{id_usuario}", response_model=List[ReservaResponse], tags=["Reservas"])
def reservas_por_usuario(id_usuario: int, db: Session = Depends(get_db)):
    # Historial de reservas de un usuario específico
    return ReservaService(db).listar_por_usuario(id_usuario)

@router.get("/reservas/{id_reserva}", response_model=ReservaResponse, tags=["Reservas"])
def obtener_reserva(id_reserva: int, db: Session = Depends(get_db)):
    r = ReservaService(db).obtener(id_reserva)
    if not r:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    return r

@router.post("/reservas", response_model=ReservaResponse, status_code=status.HTTP_201_CREATED, tags=["Reservas"])
def crear_reserva(data: ReservaCreate, db: Session = Depends(get_db)):
    return ReservaService(db).crear(
        data.id_usuario_solicita, data.id_recurso,
        data.fecha_inicio, data.fecha_fin, data.proposito,
    )

@router.patch("/reservas/{id_reserva}/aprobar", response_model=ReservaResponse, tags=["Reservas"])
def aprobar_reserva(id_reserva: int, data: ReservaAprobar, db: Session = Depends(get_db)):
    # Acción de negocio: cambia estado a "Aprobada" y registra el monitor
    r = ReservaService(db).aprobar(id_reserva, data.id_monitor_aprueba)
    if not r:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    return r

@router.patch("/reservas/{id_reserva}/rechazar", response_model=ReservaResponse, tags=["Reservas"])
def rechazar_reserva(id_reserva: int, db: Session = Depends(get_db)):
    # No necesita body: solo cambia el estado a "Rechazada"
    r = ReservaService(db).rechazar(id_reserva)
    if not r:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    return r

@router.patch("/reservas/{id_reserva}/cancelar", response_model=ReservaResponse, tags=["Reservas"])
def cancelar_reserva(id_reserva: int, db: Session = Depends(get_db)):
    r = ReservaService(db).cancelar(id_reserva)
    if not r:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    return r


# =============================================================================
# PRÉSTAMOS
# Incluye endpoint de acción: /devolucion
# =============================================================================

@router.get("/prestamos", response_model=List[PrestamoResponse], tags=["Préstamos"])
def listar_prestamos(db: Session = Depends(get_db)):
    return PrestamoService(db).listar()

@router.get("/prestamos/activos", response_model=List[PrestamoResponse], tags=["Préstamos"])
def listar_prestamos_activos(db: Session = Depends(get_db)):
    # Recursos que están actualmente fuera del laboratorio
    return PrestamoService(db).listar_activos()

@router.get("/prestamos/{id_prestamo}", response_model=PrestamoResponse, tags=["Préstamos"])
def obtener_prestamo(id_prestamo: int, db: Session = Depends(get_db)):
    p = PrestamoService(db).obtener(id_prestamo)
    if not p:
        raise HTTPException(status_code=404, detail="Préstamo no encontrado")
    return p

@router.post("/prestamos", response_model=PrestamoResponse, status_code=status.HTTP_201_CREATED, tags=["Préstamos"])
def crear_prestamo(data: PrestamoCreate, db: Session = Depends(get_db)):
    # Se llama cuando el monitor entrega físicamente el recurso
    return PrestamoService(db).crear(data.id_reserva, data.id_monitor_entrega)

@router.patch("/prestamos/{id_prestamo}/devolucion", response_model=PrestamoResponse, tags=["Préstamos"])
def registrar_devolucion(id_prestamo: int, data: PrestamoDevolucion, db: Session = Depends(get_db)):
    # Se llama cuando el estudiante devuelve el recurso
    p = PrestamoService(db).registrar_devolucion(id_prestamo, data.estado_recepcion)
    if not p:
        raise HTTPException(status_code=404, detail="Préstamo no encontrado")
    return p


# =============================================================================
# NOVEDADES
# =============================================================================

@router.get("/novedades", response_model=List[NovedadResponse], tags=["Novedades"])
def listar_novedades(db: Session = Depends(get_db)):
    return NovedadService(db).listar()

@router.get("/novedades/recurso/{id_recurso}", response_model=List[NovedadResponse], tags=["Novedades"])
def novedades_por_recurso(id_recurso: int, db: Session = Depends(get_db)):
    # Historial de incidentes de un recurso específico
    return NovedadService(db).listar_por_recurso(id_recurso)

@router.get("/novedades/{id_novedad}", response_model=NovedadResponse, tags=["Novedades"])
def obtener_novedad(id_novedad: int, db: Session = Depends(get_db)):
    n = NovedadService(db).obtener(id_novedad)
    if not n:
        raise HTTPException(status_code=404, detail="Novedad no encontrada")
    return n

@router.post("/novedades", response_model=NovedadResponse, status_code=status.HTTP_201_CREATED, tags=["Novedades"])
def crear_novedad(data: NovedadCreate, db: Session = Depends(get_db)):
    return NovedadService(db).crear(
        data.id_recurso, data.id_usuario_reporta,
        data.descripcion, data.gravedad, data.id_prestamo,
    )

@router.patch("/novedades/{id_novedad}/estado", response_model=NovedadResponse, tags=["Novedades"])
def cambiar_estado_novedad(id_novedad: int, data: NovedadEstado, db: Session = Depends(get_db)):
    n = NovedadService(db).cambiar_estado(id_novedad, data.estado)
    if not n:
        raise HTTPException(status_code=404, detail="Novedad no encontrada")
    return n


# =============================================================================
# SANCIONES
# =============================================================================

@router.get("/sanciones", response_model=List[SancionResponse], tags=["Sanciones"])
def listar_sanciones(db: Session = Depends(get_db)):
    return SancionService(db).listar()

@router.get("/sanciones/estudiante/{id_usuario}", response_model=List[SancionResponse], tags=["Sanciones"])
def sanciones_por_estudiante(id_usuario: int, db: Session = Depends(get_db)):
    # Permite verificar si un estudiante tiene sanciones activas antes de aprobar una reserva
    return SancionService(db).listar_por_estudiante(id_usuario)

@router.get("/sanciones/{id_sancion}", response_model=SancionResponse, tags=["Sanciones"])
def obtener_sancion(id_sancion: int, db: Session = Depends(get_db)):
    s = SancionService(db).obtener(id_sancion)
    if not s:
        raise HTTPException(status_code=404, detail="Sanción no encontrada")
    return s

@router.post("/sanciones", response_model=SancionResponse, status_code=status.HTTP_201_CREATED, tags=["Sanciones"])
def crear_sancion(data: SancionCreate, db: Session = Depends(get_db)):
    return SancionService(db).crear(
        data.id_usuario_estudiante, data.id_prestamo,
        data.fecha_inicio, data.fecha_fin, data.motivo,
    )

@router.patch("/sanciones/{id_sancion}/levantar", response_model=SancionResponse, tags=["Sanciones"])
def levantar_sancion(id_sancion: int, db: Session = Depends(get_db)):
    # Acción de negocio: levanta la restricción sobre el estudiante
    s = SancionService(db).levantar(id_sancion)
    if not s:
        raise HTTPException(status_code=404, detail="Sanción no encontrada")
    return s
