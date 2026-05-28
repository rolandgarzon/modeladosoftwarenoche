# =============================================================================
# api/route.py  —  CAPA API: RUTAS / ENDPOINTS
# =============================================================================
# Este archivo define todos los endpoints HTTP de la aplicación.
# Cada endpoint:
#   1. Recibe la petición HTTP y valida su body con un schema Pydantic
#   2. Obtiene una sesión de BD inyectada por Depends(get_db)
#   3. Crea el servicio correspondiente y llama al método de negocio
#   4. Devuelve la respuesta serializada con el schema de respuesta
#
# Convención de rutas usada:
#   GET    /entidades              → listar todos
#   GET    /entidades/{id}        → obtener uno por ID
#   POST   /entidades             → crear uno nuevo
#   PUT    /entidades/{id}        → actualizar campos del registro
#   PATCH  /entidades/{id}/accion → ejecutar una acción de negocio específica
#   DELETE /entidades/{id}        → eliminar
#
# IMPORTANTE: las rutas con segmentos fijos (ej: /disponibles, /pendientes)
# deben declararse ANTES que las rutas con parámetros (ej: /{id}), de lo
# contrario FastAPI intentará interpretar el segmento fijo como un ID.
# =============================================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.infraestructure.database import get_db
from src.application.services import (
    RolService, UsuarioService, EstudianteService,
    ProfesorService, MonitorService, RecursoService,
    EquipoPortatilService, LaboratorioService,
    ReservaService, PrestamoService, NovedadService, SancionService,
)
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

# APIRouter agrupa todos los endpoints de este archivo.
# main.py lo registra con app.include_router(router).
router = APIRouter()

# =============================================================================
# ROLES
# =============================================================================

@router.get("/roles", response_model=list[RolResponse], tags=["Roles"])
def listar_roles(db: Session = Depends(get_db)):
    return RolService(db).listar()


@router.get("/roles/{id_rol}", response_model=RolResponse, tags=["Roles"])
def obtener_rol(id_rol: int, db: Session = Depends(get_db)):
    rol = RolService(db).obtener(id_rol)
    if not rol:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    return rol


@router.post("/roles", response_model=RolResponse, status_code=201, tags=["Roles"])
def crear_rol(body: RolCreate, db: Session = Depends(get_db)):
    return RolService(db).crear(body.nombre_rol)


@router.delete("/roles/{id_rol}", status_code=204, tags=["Roles"])
def eliminar_rol(id_rol: int, db: Session = Depends(get_db)):
    eliminado = RolService(db).eliminar(id_rol)
    if not eliminado:
        raise HTTPException(status_code=404, detail="Rol no encontrado")


# =============================================================================
# USUARIOS
# =============================================================================

@router.get("/usuarios", response_model=list[UsuarioResponse], tags=["Usuarios"])
def listar_usuarios(db: Session = Depends(get_db)):
    return UsuarioService(db).listar()


@router.get("/usuarios/{id_usuario}", response_model=UsuarioResponse, tags=["Usuarios"])
def obtener_usuario(id_usuario: int, db: Session = Depends(get_db)):
    usuario = UsuarioService(db).obtener(id_usuario)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


@router.post("/usuarios", response_model=UsuarioResponse, status_code=201, tags=["Usuarios"])
def crear_usuario(body: UsuarioCreate, db: Session = Depends(get_db)):
    return UsuarioService(db).crear(
        id_rol=body.id_rol,
        nombre_completo=body.nombre_completo,
        correo=body.correo,
        contrasena_hash=body.contrasena_hash,
    )


@router.put("/usuarios/{id_usuario}", response_model=UsuarioResponse, tags=["Usuarios"])
def actualizar_usuario(id_usuario: int, body: UsuarioUpdate, db: Session = Depends(get_db)):
    # model_dump(exclude_none=True) omite los campos que el cliente no envió
    usuario = UsuarioService(db).actualizar(id_usuario, **body.model_dump(exclude_none=True))
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


@router.delete("/usuarios/{id_usuario}", status_code=204, tags=["Usuarios"])
def eliminar_usuario(id_usuario: int, db: Session = Depends(get_db)):
    eliminado = UsuarioService(db).eliminar(id_usuario)
    if not eliminado:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")


# =============================================================================
# ESTUDIANTES
# =============================================================================

@router.get("/estudiantes", response_model=list[EstudianteResponse], tags=["Estudiantes"])
def listar_estudiantes(db: Session = Depends(get_db)):
    return EstudianteService(db).listar()


@router.get("/estudiantes/{id_usuario}", response_model=EstudianteResponse, tags=["Estudiantes"])
def obtener_estudiante(id_usuario: int, db: Session = Depends(get_db)):
    estudiante = EstudianteService(db).obtener(id_usuario)
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    return estudiante


@router.post("/estudiantes", response_model=EstudianteResponse, status_code=201, tags=["Estudiantes"])
def crear_estudiante(body: EstudianteCreate, db: Session = Depends(get_db)):
    return EstudianteService(db).crear(
        id_usuario=body.id_usuario,
        matricula=body.matricula,
        programa=body.programa,
    )


# =============================================================================
# PROFESORES
# =============================================================================

@router.get("/profesores", response_model=list[ProfesorResponse], tags=["Profesores"])
def listar_profesores(db: Session = Depends(get_db)):
    return ProfesorService(db).listar()


@router.get("/profesores/{id_usuario}", response_model=ProfesorResponse, tags=["Profesores"])
def obtener_profesor(id_usuario: int, db: Session = Depends(get_db)):
    profesor = ProfesorService(db).obtener(id_usuario)
    if not profesor:
        raise HTTPException(status_code=404, detail="Profesor no encontrado")
    return profesor


@router.post("/profesores", response_model=ProfesorResponse, status_code=201, tags=["Profesores"])
def crear_profesor(body: ProfesorCreate, db: Session = Depends(get_db)):
    return ProfesorService(db).crear(
        id_usuario=body.id_usuario,
        departamento=body.departamento,
    )


# =============================================================================
# MONITORES
# =============================================================================

@router.get("/monitores", response_model=list[MonitorResponse], tags=["Monitores"])
def listar_monitores(db: Session = Depends(get_db)):
    return MonitorService(db).listar()


@router.get("/monitores/{id_usuario}", response_model=MonitorResponse, tags=["Monitores"])
def obtener_monitor(id_usuario: int, db: Session = Depends(get_db)):
    monitor = MonitorService(db).obtener(id_usuario)
    if not monitor:
        raise HTTPException(status_code=404, detail="Monitor no encontrado")
    return monitor


@router.post("/monitores", response_model=MonitorResponse, status_code=201, tags=["Monitores"])
def crear_monitor(body: MonitorCreate, db: Session = Depends(get_db)):
    return MonitorService(db).crear(
        id_usuario=body.id_usuario,
        id_turno=body.id_turno,
    )


# =============================================================================
# RECURSOS
# Rutas estáticas (/disponibles, /tipo/{tipo}) deben ir ANTES de /{id_recurso}
# =============================================================================

@router.get("/recursos/disponibles", response_model=list[RecursoResponse], tags=["Recursos"])
def listar_recursos_disponibles(db: Session = Depends(get_db)):
    return RecursoService(db).listar_disponibles()


@router.get("/recursos/tipo/{tipo}", response_model=list[RecursoResponse], tags=["Recursos"])
def listar_recursos_por_tipo(tipo: str, db: Session = Depends(get_db)):
    # tipo esperado: "Portatil" o "Laboratorio"
    return RecursoService(db).listar_por_tipo(tipo)


@router.get("/recursos", response_model=list[RecursoResponse], tags=["Recursos"])
def listar_recursos(db: Session = Depends(get_db)):
    return RecursoService(db).listar()


@router.get("/recursos/{id_recurso}", response_model=RecursoResponse, tags=["Recursos"])
def obtener_recurso(id_recurso: int, db: Session = Depends(get_db)):
    recurso = RecursoService(db).obtener(id_recurso)
    if not recurso:
        raise HTTPException(status_code=404, detail="Recurso no encontrado")
    return recurso


@router.post("/recursos", response_model=RecursoResponse, status_code=201, tags=["Recursos"])
def crear_recurso(body: RecursoCreate, db: Session = Depends(get_db)):
    return RecursoService(db).crear(
        id_placa=body.id_placa,
        marca=body.marca,
        estado=body.estado,
        tipo_recurso=body.tipo_recurso,
    )


@router.patch("/recursos/{id_recurso}/estado", response_model=RecursoResponse, tags=["Recursos"])
def actualizar_estado_recurso(id_recurso: int, body: RecursoEstadoUpdate, db: Session = Depends(get_db)):
    recurso = RecursoService(db).actualizar_estado(id_recurso, body.estado)
    if not recurso:
        raise HTTPException(status_code=404, detail="Recurso no encontrado")
    return recurso


@router.delete("/recursos/{id_recurso}", status_code=204, tags=["Recursos"])
def eliminar_recurso(id_recurso: int, db: Session = Depends(get_db)):
    eliminado = RecursoService(db).eliminar(id_recurso)
    if not eliminado:
        raise HTTPException(status_code=404, detail="Recurso no encontrado")


# =============================================================================
# EQUIPOS PORTÁTILES
# =============================================================================

@router.get("/equipos-portatiles", response_model=list[EquipoPortatilResponse], tags=["Equipos Portátiles"])
def listar_equipos_portatiles(db: Session = Depends(get_db)):
    return EquipoPortatilService(db).listar()


@router.get("/equipos-portatiles/{id_recurso}", response_model=EquipoPortatilResponse, tags=["Equipos Portátiles"])
def obtener_equipo_portatil(id_recurso: int, db: Session = Depends(get_db)):
    equipo = EquipoPortatilService(db).obtener(id_recurso)
    if not equipo:
        raise HTTPException(status_code=404, detail="Equipo portátil no encontrado")
    return equipo


@router.post("/equipos-portatiles", response_model=EquipoPortatilResponse, status_code=201, tags=["Equipos Portátiles"])
def crear_equipo_portatil(body: EquipoPortatilCreate, db: Session = Depends(get_db)):
    return EquipoPortatilService(db).crear(
        id_recurso=body.id_recurso,
        modelo=body.modelo,
        sistema_operativo=body.sistema_operativo,
    )


# =============================================================================
# LABORATORIOS
# =============================================================================

@router.get("/laboratorios", response_model=list[LaboratorioResponse], tags=["Laboratorios"])
def listar_laboratorios(db: Session = Depends(get_db)):
    return LaboratorioService(db).listar()


@router.get("/laboratorios/{id_recurso}", response_model=LaboratorioResponse, tags=["Laboratorios"])
def obtener_laboratorio(id_recurso: int, db: Session = Depends(get_db)):
    laboratorio = LaboratorioService(db).obtener(id_recurso)
    if not laboratorio:
        raise HTTPException(status_code=404, detail="Laboratorio no encontrado")
    return laboratorio


@router.post("/laboratorios", response_model=LaboratorioResponse, status_code=201, tags=["Laboratorios"])
def crear_laboratorio(body: LaboratorioCreate, db: Session = Depends(get_db)):
    return LaboratorioService(db).crear(
        id_recurso=body.id_recurso,
        capacidad=body.capacidad,
        ubicacion=body.ubicacion,
        software=body.software,
    )


# =============================================================================
# RESERVAS
# Rutas estáticas (/pendientes, /usuario/{id}) deben ir ANTES de /{id_reserva}
# =============================================================================

@router.get("/reservas/pendientes", response_model=list[ReservaResponse], tags=["Reservas"])
def listar_reservas_pendientes(db: Session = Depends(get_db)):
    return ReservaService(db).listar_pendientes()


@router.get("/reservas/usuario/{id_usuario}", response_model=list[ReservaResponse], tags=["Reservas"])
def listar_reservas_por_usuario(id_usuario: int, db: Session = Depends(get_db)):
    return ReservaService(db).listar_por_usuario(id_usuario)


@router.get("/reservas", response_model=list[ReservaResponse], tags=["Reservas"])
def listar_reservas(db: Session = Depends(get_db)):
    return ReservaService(db).listar()


@router.get("/reservas/{id_reserva}", response_model=ReservaResponse, tags=["Reservas"])
def obtener_reserva(id_reserva: int, db: Session = Depends(get_db)):
    reserva = ReservaService(db).obtener(id_reserva)
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    return reserva


@router.post("/reservas", response_model=ReservaResponse, status_code=201, tags=["Reservas"])
def crear_reserva(body: ReservaCreate, db: Session = Depends(get_db)):
    return ReservaService(db).crear(
        id_usuario_solicita=body.id_usuario_solicita,
        id_recurso=body.id_recurso,
        fecha_inicio=body.fecha_inicio,
        fecha_fin=body.fecha_fin,
        proposito=body.proposito,
    )


@router.patch("/reservas/{id_reserva}/aprobar", response_model=ReservaResponse, tags=["Reservas"])
def aprobar_reserva(id_reserva: int, body: ReservaAprobar, db: Session = Depends(get_db)):
    reserva = ReservaService(db).aprobar(id_reserva, body.id_monitor_aprueba)
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    return reserva


@router.patch("/reservas/{id_reserva}/rechazar", response_model=ReservaResponse, tags=["Reservas"])
def rechazar_reserva(id_reserva: int, db: Session = Depends(get_db)):
    reserva = ReservaService(db).rechazar(id_reserva)
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    return reserva


@router.patch("/reservas/{id_reserva}/cancelar", response_model=ReservaResponse, tags=["Reservas"])
def cancelar_reserva(id_reserva: int, db: Session = Depends(get_db)):
    reserva = ReservaService(db).cancelar(id_reserva)
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    return reserva


# =============================================================================
# PRÉSTAMOS
# Rutas estáticas (/activos) deben ir ANTES de /{id_prestamo}
# =============================================================================

@router.get("/prestamos/activos", response_model=list[PrestamoResponse], tags=["Préstamos"])
def listar_prestamos_activos(db: Session = Depends(get_db)):
    return PrestamoService(db).listar_activos()


@router.get("/prestamos", response_model=list[PrestamoResponse], tags=["Préstamos"])
def listar_prestamos(db: Session = Depends(get_db)):
    return PrestamoService(db).listar()


@router.get("/prestamos/{id_prestamo}", response_model=PrestamoResponse, tags=["Préstamos"])
def obtener_prestamo(id_prestamo: int, db: Session = Depends(get_db)):
    prestamo = PrestamoService(db).obtener(id_prestamo)
    if not prestamo:
        raise HTTPException(status_code=404, detail="Préstamo no encontrado")
    return prestamo


@router.post("/prestamos", response_model=PrestamoResponse, status_code=201, tags=["Préstamos"])
def crear_prestamo(body: PrestamoCreate, db: Session = Depends(get_db)):
    return PrestamoService(db).crear(
        id_reserva=body.id_reserva,
        id_monitor_entrega=body.id_monitor_entrega,
    )


@router.patch("/prestamos/{id_prestamo}/devolucion", response_model=PrestamoResponse, tags=["Préstamos"])
def registrar_devolucion(id_prestamo: int, body: PrestamoDevolucion, db: Session = Depends(get_db)):
    prestamo = PrestamoService(db).registrar_devolucion(id_prestamo, body.estado_recepcion)
    if not prestamo:
        raise HTTPException(status_code=404, detail="Préstamo no encontrado")
    return prestamo


# =============================================================================
# NOVEDADES
# =============================================================================

@router.get("/novedades/recurso/{id_recurso}", response_model=list[NovedadResponse], tags=["Novedades"])
def listar_novedades_por_recurso(id_recurso: int, db: Session = Depends(get_db)):
    return NovedadService(db).listar_por_recurso(id_recurso)


@router.get("/novedades", response_model=list[NovedadResponse], tags=["Novedades"])
def listar_novedades(db: Session = Depends(get_db)):
    return NovedadService(db).listar()


@router.get("/novedades/{id_novedad}", response_model=NovedadResponse, tags=["Novedades"])
def obtener_novedad(id_novedad: int, db: Session = Depends(get_db)):
    novedad = NovedadService(db).obtener(id_novedad)
    if not novedad:
        raise HTTPException(status_code=404, detail="Novedad no encontrada")
    return novedad


@router.post("/novedades", response_model=NovedadResponse, status_code=201, tags=["Novedades"])
def crear_novedad(body: NovedadCreate, db: Session = Depends(get_db)):
    return NovedadService(db).crear(
        id_recurso=body.id_recurso,
        id_usuario_reporta=body.id_usuario_reporta,
        descripcion=body.descripcion,
        gravedad=body.gravedad,
        id_prestamo=body.id_prestamo,
    )


@router.patch("/novedades/{id_novedad}/estado", response_model=NovedadResponse, tags=["Novedades"])
def cambiar_estado_novedad(id_novedad: int, body: NovedadEstado, db: Session = Depends(get_db)):
    novedad = NovedadService(db).cambiar_estado(id_novedad, body.estado)
    if not novedad:
        raise HTTPException(status_code=404, detail="Novedad no encontrada")
    return novedad


# =============================================================================
# SANCIONES
# =============================================================================

@router.get("/sanciones/estudiante/{id_usuario}", response_model=list[SancionResponse], tags=["Sanciones"])
def listar_sanciones_por_estudiante(id_usuario: int, db: Session = Depends(get_db)):
    return SancionService(db).listar_por_estudiante(id_usuario)


@router.get("/sanciones", response_model=list[SancionResponse], tags=["Sanciones"])
def listar_sanciones(db: Session = Depends(get_db)):
    return SancionService(db).listar()


@router.get("/sanciones/{id_sancion}", response_model=SancionResponse, tags=["Sanciones"])
def obtener_sancion(id_sancion: int, db: Session = Depends(get_db)):
    sancion = SancionService(db).obtener(id_sancion)
    if not sancion:
        raise HTTPException(status_code=404, detail="Sanción no encontrada")
    return sancion


@router.post("/sanciones", response_model=SancionResponse, status_code=201, tags=["Sanciones"])
def crear_sancion(body: SancionCreate, db: Session = Depends(get_db)):
    return SancionService(db).crear(
        id_usuario_estudiante=body.id_usuario_estudiante,
        id_prestamo=body.id_prestamo,
        fecha_inicio=body.fecha_inicio,
        fecha_fin=body.fecha_fin,
        motivo=body.motivo,
    )


@router.patch("/sanciones/{id_sancion}/levantar", response_model=SancionResponse, tags=["Sanciones"])
def levantar_sancion(id_sancion: int, db: Session = Depends(get_db)):
    sancion = SancionService(db).levantar(id_sancion)
    if not sancion:
        raise HTTPException(status_code=404, detail="Sanción no encontrada")
    return sancion
