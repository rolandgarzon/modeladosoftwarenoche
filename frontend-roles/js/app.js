/**
 * app.js — Lógica principal del frontend para la gestión de roles.
 *
 * Responsabilidades:
 *  - Comunicarse con la API REST (FastAPI en backend) para listar, crear y eliminar roles.
 *  - Renderizar dinámicamente la tabla de roles en el DOM.
 *  - Manejar el flujo de confirmación de eliminación mediante un modal.
 *  - Mostrar el estado de conectividad con la API en tiempo real.
 */

// URL base del backend FastAPI desplegado en Render.
// La versión localhost queda comentada para desarrollo local.
const API_BASE = 'http://localhost:8000';


// ===== Referencias al DOM =====
// Se capturan una sola vez al cargar el script para evitar búsquedas repetidas en el DOM.

const apiStatus   = document.getElementById('api-status');   // Indicador visual de conexión con la API
const formCrear   = document.getElementById('form-crear');    // Formulario para crear un nuevo rol
const inputNombre = document.getElementById('nombre-rol');    // Campo de texto con el nombre del rol
const msgCrear    = document.getElementById('msg-crear');     // Zona de mensajes del formulario de creación
const tbodyRoles  = document.getElementById('tbody-roles');   // Cuerpo de la tabla donde se listan los roles
const msgLista    = document.getElementById('msg-lista');     // Zona de mensajes de la sección de listado
const btnRecargar = document.getElementById('btn-recargar'); // Botón para recargar la lista manualmente

// Elementos del modal de confirmación de eliminación
const modal        = document.getElementById('modal-confirm'); // Contenedor del modal
const modalBody    = document.getElementById('modal-body');    // Texto descriptivo dentro del modal
const btnConfirmar = document.getElementById('btn-confirmar'); // Botón que confirma la eliminación
const btnCancelar  = document.getElementById('btn-cancelar');  // Botón que cancela la operación

// Almacena temporalmente el ID del rol que el usuario intenta eliminar
// hasta que confirme o cancele en el modal.
let rolPendienteId = null;

// ===== Utilidades =====

/**
 * Muestra un mensaje en el elemento dado con una clase CSS según el tipo.
 * @param {HTMLElement} el   - Elemento donde se mostrará el mensaje.
 * @param {string}      texto - Texto del mensaje.
 * @param {string}      tipo  - Tipo de mensaje: 'success' | 'error' | 'info'.
 */
function setMsg(el, texto, tipo) {
  el.textContent = texto;
  el.className = `msg msg--${tipo}`;
}

/**
 * Limpia el contenido y las clases de un elemento de mensaje,
 * dejándolo vacío y sin estilo de estado.
 * @param {HTMLElement} el - Elemento a limpiar.
 */
function clearMsg(el) {
  el.textContent = '';
  el.className = 'msg';
}

/**
 * Actualiza el indicador de estado de la API en la interfaz.
 * Cambia el texto y la clase CSS del badge según si la API está en línea o no.
 * @param {boolean} online - true si la API responde correctamente, false si no.
 */
function setApiStatus(online) {
  apiStatus.textContent = online ? 'API conectada' : 'API desconectada';
  apiStatus.className   = `badge badge--${online ? 'on' : 'off'}`;
}

// ===== Peticiones a la API =====

/**
 * Obtiene la lista completa de roles desde el backend.
 * Lanza un Error si la respuesta HTTP no es exitosa (status fuera del rango 200-299).
 * @returns {Promise<Array>} Array de objetos rol con al menos { id_rol, nombre_rol }.
 */
async function fetchRoles() {
  const res = await fetch(`${API_BASE}/roles`);
  if (!res.ok) throw new Error(`Error ${res.status}`);
  return res.json();
}

/**
 * Envía una petición POST para crear un nuevo rol en el backend.
 * Si el servidor devuelve un error, intenta extraer el campo `detail` del JSON
 * para mostrar un mensaje más descriptivo al usuario.
 * @param {string} nombreRol - Nombre del rol a crear.
 * @returns {Promise<Object>} Objeto del rol recién creado: { id_rol, nombre_rol }.
 */
async function crearRol(nombreRol) {
  const res = await fetch(`${API_BASE}/roles`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ nombre_rol: nombreRol }),
  });
  if (!res.ok) {
    // Intenta parsear el body del error; si falla, usa un objeto vacío como fallback.
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Error ${res.status}`);
  }
  return res.json();
}

/**
 * Envía una petición DELETE para eliminar un rol por su ID.
 * El backend responde con 204 No Content en caso de éxito, por lo que no se parsea el body.
 * Si la respuesta indica error, se extrae el campo `detail` del JSON para informar al usuario.
 * @param {number} idRol - ID numérico del rol a eliminar.
 */
async function eliminarRol(idRol) {
  const res = await fetch(`${API_BASE}/roles/${idRol}`, { method: 'DELETE' });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Error ${res.status}`);
  }
  // 204 No Content → el servidor no devuelve body, no se llama res.json()
}

// ===== Renderizado de la tabla =====

/**
 * Genera y vuelca el HTML de las filas de la tabla de roles.
 * Si no hay roles, muestra una fila con un mensaje informativo.
 * Cada fila incluye un botón "Eliminar" con los atributos data-id y data-nombre
 * que luego son leídos por la delegación de eventos en tbodyRoles.
 * @param {Array} roles - Lista de objetos rol: [{ id_rol, nombre_rol }, ...].
 */
function renderTabla(roles) {
  if (roles.length === 0) {
    tbodyRoles.innerHTML = '<tr><td colspan="3" class="empty">No hay roles registrados.</td></tr>';
    return;
  }

  tbodyRoles.innerHTML = roles
    .map(
      (r) => `
      <tr>
        <td>${r.id_rol}</td>
        <td>${escapeHtml(r.nombre_rol)}</td>
        <td>
          <button
            class="btn btn--danger btn--icon"
            data-id="${r.id_rol}"
            data-nombre="${escapeHtml(r.nombre_rol)}"
            title="Eliminar rol"
          >Eliminar</button>
        </td>
      </tr>`
    )
    .join('');
}

/**
 * Escapa caracteres especiales de HTML para prevenir XSS al insertar
 * texto dinámico procedente del servidor dentro del innerHTML.
 * Cubre los caracteres: & < > "
 * @param {string} str - Cadena de texto a escapar.
 * @returns {string} Cadena con entidades HTML sustituidas.
 */
function escapeHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// ===== Carga de roles =====

/**
 * Carga la lista de roles desde la API y actualiza la tabla en el DOM.
 * Flujo:
 *  1. Muestra un indicador de "Cargando…" y desactiva el botón recargar.
 *  2. Llama a fetchRoles(); si tiene éxito, marca la API como conectada y renderiza.
 *  3. Si hay error, marca la API como desconectada y muestra el mensaje de error.
 *  4. En cualquier caso, reactiva el botón recargar al finalizar (bloque finally).
 */
async function cargarRoles() {
  clearMsg(msgLista);
  tbodyRoles.innerHTML = '<tr><td colspan="3" class="empty">Cargando…</td></tr>';
  btnRecargar.disabled = true;

  try {
    const roles = await fetchRoles();
    setApiStatus(true);
    renderTabla(roles);
  } catch (e) {
    setApiStatus(false);
    tbodyRoles.innerHTML = '<tr><td colspan="3" class="empty">No se pudo conectar con la API.</td></tr>';
    setMsg(msgLista, e.message, 'error');
  } finally {
    btnRecargar.disabled = false;
  }
}

// ===== Crear rol =====

/**
 * Maneja el envío del formulario de creación de rol.
 * Pasos:
 *  1. Previene la recarga de página por defecto del formulario.
 *  2. Valida que el campo no esté vacío (trim para ignorar espacios).
 *  3. Desactiva el botón mientras la petición está en vuelo para evitar doble envío.
 *  4. Llama a crearRol(); en caso de éxito muestra confirmación y recarga la tabla.
 *  5. Restaura el botón en el bloque finally sin importar el resultado.
 */
formCrear.addEventListener('submit', async (e) => {
  e.preventDefault();
  clearMsg(msgCrear);

  const nombre = inputNombre.value.trim();
  if (!nombre) return; // No se envía si el campo está vacío o solo tiene espacios

  const btnSubmit = formCrear.querySelector('button[type="submit"]');
  btnSubmit.disabled = true;
  btnSubmit.textContent = 'Creando…';

  try {
    const nuevo = await crearRol(nombre);
    setMsg(msgCrear, `Rol "${nuevo.nombre_rol}" creado con ID ${nuevo.id_rol}.`, 'success');
    inputNombre.value = '';       // Limpia el campo tras la creación exitosa
    await cargarRoles();          // Refresca la tabla para mostrar el nuevo rol
  } catch (e) {
    setMsg(msgCrear, `Error: ${e.message}`, 'error');
  } finally {
    btnSubmit.disabled = false;
    btnSubmit.textContent = 'Crear';
  }
});

// ===== Eliminar rol (delegación de eventos + modal) =====

/**
 * Delegación de eventos sobre el tbody: en lugar de asignar un listener a cada
 * botón "Eliminar" individual (que se recrean en cada renderizado), se escucha
 * el evento en el contenedor padre y se identifica el botón con closest().
 *
 * Al hacer clic en un botón de eliminar:
 *  1. Se guarda el ID del rol en rolPendienteId.
 *  2. Se personaliza el texto del modal con el nombre e ID del rol.
 *  3. Se muestra el modal de confirmación.
 */
tbodyRoles.addEventListener('click', (e) => {
  const btn = e.target.closest('button[data-id]');
  if (!btn) return; // El clic no fue sobre un botón de eliminar

  rolPendienteId = parseInt(btn.dataset.id, 10);
  const nombre   = btn.dataset.nombre;

  modalBody.textContent = `¿Seguro que deseas eliminar el rol "${nombre}" (ID: ${rolPendienteId})?`;
  modal.hidden = false;
});

/**
 * Cierra el modal sin realizar ninguna acción cuando el usuario pulsa "Cancelar".
 * Resetea rolPendienteId para evitar eliminar un rol en un evento futuro.
 */
btnCancelar.addEventListener('click', () => {
  modal.hidden = true;
  rolPendienteId = null;
});

/**
 * Permite cerrar el modal haciendo clic en el backdrop (fondo oscuro fuera del cuadro).
 * Solo se cierra si el clic fue directamente sobre el elemento modal y no sobre su contenido.
 */
modal.addEventListener('click', (e) => {
  if (e.target === modal) {
    modal.hidden = true;
    rolPendienteId = null;
  }
});

/**
 * Ejecuta la eliminación del rol cuando el usuario confirma en el modal.
 * Pasos:
 *  1. Verifica que haya un ID pendiente (guarda contra clics fuera de flujo).
 *  2. Cierra el modal de inmediato para dar feedback visual rápido.
 *  3. Llama a eliminarRol(); en caso de éxito muestra confirmación y recarga la tabla.
 *  4. En el bloque finally, siempre resetea rolPendienteId.
 */
btnConfirmar.addEventListener('click', async () => {
  if (rolPendienteId === null) return;

  modal.hidden = true;
  clearMsg(msgLista);

  try {
    await eliminarRol(rolPendienteId);
    setMsg(msgLista, `Rol ID ${rolPendienteId} eliminado correctamente.`, 'success');
    await cargarRoles(); // Refresca la tabla para reflejar la eliminación
  } catch (e) {
    setMsg(msgLista, `Error al eliminar: ${e.message}`, 'error');
  } finally {
    rolPendienteId = null;
  }
});

// ===== Botón recargar =====

// Recarga la lista completa de roles bajo demanda cuando el usuario lo solicita.
btnRecargar.addEventListener('click', cargarRoles);

// ===== Carga inicial =====

// Ejecuta la carga de roles en cuanto el script termina de parsear,
// asegurando que la tabla esté poblada desde el primer renderizado de la página.
cargarRoles();
