# =============================================================================
# domain/models.py  —  CAPA DE DOMINIO: MODELOS ORM (ENTIDADES)
# =============================================================================
# En la arquitectura N-capas, el dominio representa las entidades del negocio.
# Cada clase aquí es un modelo ORM: un espejo en Python de una tabla en MySQL.
#
# ¿Cómo funciona?
#   - Cada clase hereda de Base (definida en database.py)
#   - __tablename__ indica a qué tabla de la BD corresponde
#   - Cada atributo con mapped_column() corresponde a una columna
#   - relationship() define cómo se navega entre tablas relacionadas
#
# Patrón de herencia de tabla usado en este proyecto:
#   USUARIOS  ──┬──► ESTUDIANTES  (un usuario puede ser estudiante)
#               ├──► PROFESORES   (o puede ser profesor)
#               └──► MONITORES    (o puede ser monitor)
#
#   RECURSOS  ──┬──► EQUIPOS_PORTATILES
#               └──► LABORATORIOS
#
# Esto se llama "Concrete Table Inheritance": la tabla hija comparte
# la PK con la tabla padre en lugar de generar su propio ID.
# =============================================================================

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

# Importamos la clase Base desde la capa de infraestructura
from src.infraestructure.database import Base


# =============================================================================
# ROL
# Tabla de catálogo que define los tipos de usuario del sistema.
# Ejemplos de valores: "Estudiante", "Profesor", "Monitor", "Admin"
# =============================================================================
class Rol(Base):
    __tablename__ = "ROLES"

    # primary_key=True → esta columna es la llave primaria de la tabla
    # autoincrement=True → la BD asigna el valor automáticamente (1, 2, 3...)
    id_rol: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre_rol: Mapped[str] = mapped_column(String(50))

    # Relación inversa: desde un Rol podemos acceder a la lista de sus usuarios
    # back_populates="rol" conecta con el atributo "rol" de la clase Usuario
    usuarios: Mapped[List["Usuario"]] = relationship(back_populates="rol")


# =============================================================================
# USUARIO
# Tabla base para todas las personas que usan el sistema.
# Los campos específicos de cada tipo de usuario están en tablas separadas.
# =============================================================================
class Usuario(Base):
    __tablename__ = "USUARIOS"

    id_usuario: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # ForeignKey("ROLES.id_rol") crea la llave foránea que referencia la tabla ROLES
    id_rol: Mapped[int] = mapped_column(ForeignKey("ROLES.id_rol"))

    nombre_completo: Mapped[str] = mapped_column(String(150))

    # unique=True garantiza que no puedan existir dos usuarios con el mismo correo
    correo: Mapped[str] = mapped_column(String(100), unique=True)

    # Nunca guardar contraseñas en texto plano. Este campo almacena el hash (resultado
    # de aplicar un algoritmo como bcrypt a la contraseña original).
    contrasena_hash: Mapped[str] = mapped_column(String(255))

    # Relaciones hacia la tabla ROLES y hacia las tablas hijas
    rol: Mapped["Rol"] = relationship(back_populates="usuarios")

    # uselist=False indica relación uno-a-uno: un usuario tiene UN solo perfil de estudiante
    estudiante: Mapped[Optional["Estudiante"]] = relationship(back_populates="usuario", uselist=False)
    profesor: Mapped[Optional["Profesor"]] = relationship(back_populates="usuario", uselist=False)
    monitor: Mapped[Optional["Monitor"]] = relationship(back_populates="usuario", uselist=False)


# =============================================================================
# ESTUDIANTE
# Extiende a Usuario con datos académicos específicos.
# Su PK (id_usuario) es también FK hacia USUARIOS → herencia de tabla.
# =============================================================================
class Estudiante(Base):
    __tablename__ = "ESTUDIANTES"

    # Al ser PK y FK al mismo tiempo, este campo vincula al estudiante con su usuario base
    id_usuario: Mapped[int] = mapped_column(ForeignKey("USUARIOS.id_usuario"), primary_key=True)
    matricula: Mapped[str] = mapped_column(String(50), unique=True)
    programa: Mapped[str] = mapped_column(String(100))

    usuario: Mapped["Usuario"] = relationship(back_populates="estudiante")

    # Un estudiante puede acumular múltiples sanciones a lo largo del tiempo
    sanciones: Mapped[List["Sancion"]] = relationship(back_populates="estudiante")


# =============================================================================
# PROFESOR
# Extiende a Usuario con su departamento académico.
# =============================================================================
class Profesor(Base):
    __tablename__ = "PROFESORES"

    id_usuario: Mapped[int] = mapped_column(ForeignKey("USUARIOS.id_usuario"), primary_key=True)
    departamento: Mapped[str] = mapped_column(String(100))

    usuario: Mapped["Usuario"] = relationship(back_populates="profesor")


# =============================================================================
# MONITOR
# Persona encargada de gestionar los préstamos en el laboratorio.
# Puede aprobar reservas y entregar/recibir equipos.
# =============================================================================
class Monitor(Base):
    __tablename__ = "MONITORES"

    id_usuario: Mapped[int] = mapped_column(ForeignKey("USUARIOS.id_usuario"), primary_key=True)

    # id_turno identifica en qué turno trabaja este monitor (mañana, tarde, noche, etc.)
    id_turno: Mapped[int] = mapped_column(Integer)

    usuario: Mapped["Usuario"] = relationship(back_populates="monitor")

    # foreign_keys es necesario cuando hay más de una FK hacia la misma tabla
    # en una relación. Aquí especificamos cuál FK usar para "reservas_aprobadas".
    reservas_aprobadas: Mapped[List["Reserva"]] = relationship(
        back_populates="monitor_aprueba", foreign_keys="[Reserva.id_monitor_aprueba]"
    )

    # Lista de todos los préstamos que este monitor ha entregado físicamente
    prestamos_entregados: Mapped[List["Prestamo"]] = relationship(back_populates="monitor_entrega")


# =============================================================================
# RECURSO
# Tabla base para cualquier bien físico que se puede prestar.
# Los detalles técnicos están en EQUIPOS_PORTATILES o LABORATORIOS.
# =============================================================================
class Recurso(Base):
    __tablename__ = "RECURSOS"

    id_recurso: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # id_placa es el código físico que tiene el equipo (etiqueta, sticker, etc.)
    id_placa: Mapped[str] = mapped_column(String(50), unique=True)

    marca: Mapped[str] = mapped_column(String(100))

    # estado posibles: "Disponible", "Prestado", "En mantenimiento", "Dado de baja"
    estado: Mapped[str] = mapped_column(String(50))

    # tipo_recurso indica si es "Portatil" o "Laboratorio"
    tipo_recurso: Mapped[str] = mapped_column(String(50))

    # uselist=False porque un recurso tiene un solo subtipo (portátil O laboratorio, no ambos)
    equipo_portatil: Mapped[Optional["EquipoPortatil"]] = relationship(back_populates="recurso", uselist=False)
    laboratorio: Mapped[Optional["Laboratorio"]] = relationship(back_populates="recurso", uselist=False)

    # Un recurso puede tener muchas reservas y novedades a lo largo del tiempo
    reservas: Mapped[List["Reserva"]] = relationship(back_populates="recurso")
    novedades: Mapped[List["Novedad"]] = relationship(back_populates="recurso")


# =============================================================================
# EQUIPO PORTÁTIL
# Detalles técnicos de un portátil. Su PK es también FK hacia RECURSOS.
# =============================================================================
class EquipoPortatil(Base):
    __tablename__ = "EQUIPOS_PORTATILES"

    id_recurso: Mapped[int] = mapped_column(ForeignKey("RECURSOS.id_recurso"), primary_key=True)
    modelo: Mapped[str] = mapped_column(String(100))

    # Ejemplo: "Windows 11", "Ubuntu 22.04", "macOS Ventura"
    sistema_operativo: Mapped[str] = mapped_column(String(50))

    recurso: Mapped["Recurso"] = relationship(back_populates="equipo_portatil")


# =============================================================================
# LABORATORIO
# Detalles físicos de una sala de laboratorio.
# =============================================================================
class Laboratorio(Base):
    __tablename__ = "LABORATORIOS"

    id_recurso: Mapped[int] = mapped_column(ForeignKey("RECURSOS.id_recurso"), primary_key=True)
    capacidad: Mapped[int] = mapped_column(Integer)

    # Optional[str] significa que este campo puede ser NULL en la BD
    software: Mapped[Optional[str]] = mapped_column(String(255))

    ubicacion: Mapped[str] = mapped_column(String(100))

    recurso: Mapped["Recurso"] = relationship(back_populates="laboratorio")


# =============================================================================
# RESERVA
# Solicitud formal de uso de un recurso en un rango de tiempo.
# Ciclo de vida: Pendiente → Aprobada/Rechazada → (si Aprobada) genera un Préstamo
# =============================================================================
class Reserva(Base):
    __tablename__ = "RESERVAS"

    id_reserva: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_usuario_solicita: Mapped[int] = mapped_column(ForeignKey("USUARIOS.id_usuario"))
    id_recurso: Mapped[int] = mapped_column(ForeignKey("RECURSOS.id_recurso"))

    # NULL mientras la reserva está Pendiente; se llena cuando un monitor la aprueba
    id_monitor_aprueba: Mapped[Optional[int]] = mapped_column(ForeignKey("MONITORES.id_usuario"))

    fecha_inicio: Mapped[datetime] = mapped_column(DateTime)
    fecha_fin: Mapped[datetime] = mapped_column(DateTime)

    # Estado por defecto al crearse: "Pendiente"
    # Otros valores posibles: "Aprobada", "Rechazada", "Cancelada"
    estado: Mapped[str] = mapped_column(String(50), default="Pendiente")

    proposito: Mapped[str] = mapped_column(String(255))

    # Cuando hay varias FK hacia la misma tabla (id_usuario_solicita y potencialmente
    # id_monitor_aprueba que apunta a MONITORES), SQLAlchemy necesita saber
    # qué FK usar para cada relationship → se indica con foreign_keys=[]
    usuario_solicita: Mapped["Usuario"] = relationship(foreign_keys=[id_usuario_solicita])
    recurso: Mapped["Recurso"] = relationship(back_populates="reservas")
    monitor_aprueba: Mapped[Optional["Monitor"]] = relationship(
        back_populates="reservas_aprobadas", foreign_keys=[id_monitor_aprueba]
    )

    # Una reserva aprobada origina exactamente un préstamo (relación uno-a-uno)
    prestamo: Mapped[Optional["Prestamo"]] = relationship(back_populates="reserva", uselist=False)


# =============================================================================
# PRÉSTAMO
# Registro del momento físico en que se entrega y se devuelve un recurso.
# Cada préstamo nace de una reserva previamente aprobada.
# =============================================================================
class Prestamo(Base):
    __tablename__ = "PRESTAMOS"

    id_prestamo: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # unique=True garantiza que una reserva no pueda generar más de un préstamo
    id_reserva: Mapped[int] = mapped_column(ForeignKey("RESERVAS.id_reserva"), unique=True)

    # Monitor que entregó físicamente el recurso al solicitante
    id_monitor_entrega: Mapped[int] = mapped_column(ForeignKey("MONITORES.id_usuario"))

    hora_entrega: Mapped[datetime] = mapped_column(DateTime)

    # NULL mientras el recurso no ha sido devuelto (préstamo activo)
    hora_devolucion: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Estado del recurso al ser devuelto: "Bueno", "Con daños", "Incompleto", etc.
    estado_recepcion: Mapped[Optional[str]] = mapped_column(String(50))

    reserva: Mapped["Reserva"] = relationship(back_populates="prestamo")
    monitor_entrega: Mapped["Monitor"] = relationship(back_populates="prestamos_entregados")
    novedades: Mapped[List["Novedad"]] = relationship(back_populates="prestamo")
    sanciones: Mapped[List["Sancion"]] = relationship(back_populates="prestamo")


# =============================================================================
# NOVEDAD
# Registro de un incidente o daño detectado en un recurso.
# Puede estar asociada a un préstamo concreto o reportarse de forma independiente.
# =============================================================================
class Novedad(Base):
    __tablename__ = "NOVEDADES"

    id_novedad: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_recurso: Mapped[int] = mapped_column(ForeignKey("RECURSOS.id_recurso"))
    id_usuario_reporta: Mapped[int] = mapped_column(ForeignKey("USUARIOS.id_usuario"))

    # Puede ser NULL si la novedad no está ligada a un préstamo específico
    id_prestamo: Mapped[Optional[int]] = mapped_column(ForeignKey("PRESTAMOS.id_prestamo"))

    fecha_reporte: Mapped[datetime] = mapped_column(DateTime)

    # Text (en lugar de String) permite textos largos sin límite fijo de caracteres
    descripcion: Mapped[str] = mapped_column(Text)

    # gravedad posibles: "Leve", "Moderada", "Grave"
    gravedad: Mapped[str] = mapped_column(String(50))

    # estado posibles: "Reportada", "En revisión", "Resuelta"
    estado: Mapped[str] = mapped_column(String(50), default="Reportada")

    recurso: Mapped["Recurso"] = relationship(back_populates="novedades")
    usuario_reporta: Mapped["Usuario"] = relationship(foreign_keys=[id_usuario_reporta])
    prestamo: Mapped[Optional["Prestamo"]] = relationship(back_populates="novedades")


# =============================================================================
# SANCIÓN
# Restricción temporal aplicada a un estudiante como consecuencia de un
# incidente (daño a un equipo, no devolución a tiempo, etc.).
# =============================================================================
class Sancion(Base):
    __tablename__ = "SANCIONES"

    id_sancion: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Una sanción siempre se aplica a un estudiante (no a profesores/monitores)
    id_usuario_estudiante: Mapped[int] = mapped_column(ForeignKey("ESTUDIANTES.id_usuario"))

    # La sanción está ligada al préstamo que la originó
    id_prestamo: Mapped[int] = mapped_column(ForeignKey("PRESTAMOS.id_prestamo"))

    fecha_inicio: Mapped[datetime] = mapped_column(DateTime)
    fecha_fin: Mapped[datetime] = mapped_column(DateTime)
    motivo: Mapped[str] = mapped_column(String(255))

    # estado posibles: "Activa", "Levantada"
    estado: Mapped[str] = mapped_column(String(50), default="Activa")
    
    estudiante: Mapped["Estudiante"] = relationship(back_populates="sanciones")
    prestamo: Mapped["Prestamo"] = relationship(back_populates="sanciones")


