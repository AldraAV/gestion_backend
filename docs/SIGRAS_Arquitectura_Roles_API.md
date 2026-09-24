# SIGRAS — Arquitectura de Roles, API y Modelo de Datos
## Sistema Inteligente de Gestión de Rutas seguras para la población civil
Equipo TLAMATI-ITSNA · HackaTec Regional 2026 · Convención de rutas: `/api/v1`

---

## 1. Jerarquías de roles: 6

| # | Rol | Alcance |
|---|---|---|
| 1 | Usuario final sensible | Público, sin auth |
| 2 | Persona albergada | Estado derivado del rol 1, no tiene sesión propia |
| 3 | Coordinador de emergencias | Admin, IA exclusiva |
| 4 | Administrador de albergue | Admin, alcance = 1 albergue |
| 5 | Responsable de área | Admin, alcance = 1 área dentro de 1 albergue |
| 6 | Personal operativo | Admin, alcance = tareas dentro de 1 área |

---

## 2. Qué desempeña cada rol

**1. Usuario final sensible** — consulta mapa, rutas seguras y centros de ayuda; envía reporte sin iniciar sesión; recibe folio; consulta estado de su reporte. Puede convertirse en Persona albergada al ingresar a un refugio.

**2. Persona albergada** — usuario registrado operativamente dentro de un albergue. No administra nada. Estados posibles: `albergado`, `salida_temporal`, `egreso_definitivo`, `trasladado`. Su estado lo cambia el rol 4/5, nunca ella misma.

**3. Coordinador de emergencias** — recibe y valida reportes, los clasifica, tiene uso exclusivo de la IA vía tool_calling (actualiza Mapbox/mapa, marca incidencias, delimita zonas de riesgo, calcula rutas, delega brigadas, publica alertas con autorización).

**4. Administrador de albergue** — control total del albergue: capacidad, áreas, personas albergadas, coordina responsables.

**5. Responsable de área** — gestiona una sola área funcional (ej. médica, alimentación, psicológica): actualiza necesidades y estado del área, coordina al personal asignado.

**6. Personal operativo** — ejecuta tareas dentro de un área, registra actividades, actualiza incidencias operativas.

---

## 3. Rutas de API (v1)

### Rol 1 — Usuario final sensible (público, sin auth)
```
GET  /api/v1/publico/albergues/cercanos
GET  /api/v1/publico/mapa/incidencias
GET  /api/v1/publico/mapa/zonas-riesgo
POST /api/v1/publico/reportes
GET  /api/v1/publico/reportes/{folio}
POST /api/v1/publico/rutas/segura
```

### Rol 2 — Persona albergada
Sin rutas propias. Su estado se modifica solo desde las rutas de los roles 4/5 (`PATCH /api/v1/admin/albergues/{id}/personas/{persona_id}/estado`). No exponer un endpoint que el ciudadano pueda tocar para su propio estado.

### Autenticación (roles 3–6)
```
POST /api/v1/auth/login
```

### Rol 3 — Coordinador de emergencias
```
GET  /api/v1/admin/reportes
POST /api/v1/admin/incidencias/{id}/validar
POST /api/v1/admin/incidencias/{id}/asignar
POST /api/v1/admin/zonas-riesgo
POST /api/v1/admin/alertas
POST /api/v1/admin/ia/accion-mapa
```

### Rol 4 — Administrador de albergue
```
GET   /api/v1/admin/albergues/{id}/personas
POST  /api/v1/admin/albergues/{id}/personas
PATCH /api/v1/admin/albergues/{id}/personas/{persona_id}/estado
PATCH /api/v1/admin/albergues/{id}/capacidad
POST  /api/v1/admin/albergues/{id}/areas
```

### Rol 5 — Responsable de área
```
GET   /api/v1/admin/areas/{id}/personal
PATCH /api/v1/admin/areas/{id}/necesidades
PATCH /api/v1/admin/areas/{id}/estado
```

### Rol 6 — Personal operativo
```
POST  /api/v1/admin/areas/{id}/actividades
PATCH /api/v1/admin/incidencias-operativas/{id}
```

---

## 4. Lógica por entidad/adaptador (conceptual, sin código)

- **Reporte** — el adaptador genera el folio, filtra honeypot, aplica rate limit por IP, persiste con estado `recibido`. El servicio de consulta pública solo expone folio/estado/fecha — nunca los campos sensibles completos, aunque el modelo los tenga guardados.
- **Incidencia** — se promueve desde un Reporte validado por el Coordinador. No es 1:1: un Reporte puede no convertirse en Incidencia (duplicado, falso positivo), así que la FK a `reporte_id` debe ser nullable.
- **ZonaRiesgo** — geometría real (polígono), no JSON suelto. La crea/actualiza el Coordinador, potencialmente vía IA. Debe tener `activa` y `expira_en` — una inundación de hace 3 semanas no debería seguir bloqueando rutas hoy si nadie la desactivó.
- **Albergue** — capacidad total vs. disponible como dos campos separados. No calcular disponible restando personas en cada query; mantenerlo como contador actualizado en la misma transacción de ingreso/egreso — más barato y evita condiciones de carrera en pico de emergencia.
- **Área** — pertenece a un Albergue, tiene un `responsable_id`, expone `necesidades` como campo libre o catálogo corto (médica, alimentación, psicológica...).
- **PersonaAlbergada** — FK opcional a `reportes.folio` (puede llegar directo al albergue sin haber reportado antes). Estado como enum controlado por la base de datos, no por el backend a discreción, para evitar que un bug deje a alguien en un estado inválido.
- **HistorialEstadosPersona** — tabla de auditoría: cada cambio de estado de una persona albergada queda registrado con quién lo hizo. Mismo patrón de trazabilidad que ya usan en la ruta de auditoría de SIGEDI/Lucero; aquí aplica con más razón porque son datos de personas vulnerables.
- **AccionesIA** — log de cada llamada de tool_calling del Coordinador: qué pidió, qué ejecutó el modelo, qué cambió en el mapa. Sin esto no se le puede explicar a un jurado (ni a un auditor real) por qué el sistema marcó una zona como riesgo.
- **ServicioRutas** — interfaz `RutaProvider` que abstrae al proveedor real de ruteo. No amarrar el código a un proveedor específico dentro de ningún controlador — así cambiar de proveedor es una sola clase, no una reescritura.

---

## 5. Tablas

```sql
usuarios_admin             (id, nombre, correo, hash_password, rol, alcance_id, creado_en)

reportes                   (id, folio, municipio, tipo_necesidad, descripcion, lat, lng,
                             num_personas, personas_vulnerables, foto_path, audio_path,
                             estado, creado_en, actualizado_en)

incidencias                (id, reporte_id FK nullable, tipo, geometria, estado,
                             validado_por FK usuarios_admin, creado_en)

zonas_riesgo                (id, nombre, geometria, activa, creado_por, creado_en, expira_en)

albergues                   (id, nombre, lat, lng, capacidad_total, capacidad_disponible, municipio)

areas                       (id, albergue_id FK, nombre, responsable_id FK, necesidades, estado)

personas_albergadas         (id, folio_origen FK nullable, identidad, integrantes_grupo,
                             necesidades_medicas, estado, albergue_id FK, area_id FK,
                             creado_en, actualizado_en)

historial_estados_persona   (id, persona_id FK, estado_anterior, estado_nuevo,
                             cambiado_por, fecha)

brigadas_asignaciones        (id, incidencia_id FK, brigada, delegado_por, estado)

acciones_ia                  (id, coordinador_id FK, tipo_accion, payload, resultado, creado_en)
```

---

## 6. Tecnologías si no se usa Mapbox

> Mapbox Directions API no soporta exclusión nativa de polígonos de riesgo — solo excluye puntos individuales (función beta `exclude=point(lon,lat)`, máx. 50, limitada a perfiles driving). Para el requisito de "evitar zona de riesgo completa" hace falta otro proveedor o un workaround.

| Necesidad | Reemplazo de Mapbox |
|---|---|
| Mapa visual (tiles, marcadores) | **MapLibre GL JS** — fork open source de Mapbox GL JS, API casi idéntica, sin llave de pago, tiles de OpenStreetMap |
| Cálculo de rutas evitando polígonos | **OpenRouteService (ORS)** — soporta `avoid_polygons` nativo; API pública gratuita, autohospedable en Docker si crece el volumen |
| Geocodificación (texto → coordenadas) | **Nominatim / Photon** — abiertos |
| Almacenar y consultar geometrías (zonas de riesgo, "albergue más cercano") | **PostGIS** (extensión de Postgres, ya disponible en Supabase) — usar `ST_Distance` en la base de datos en vez de traer todos los registros a Python |
