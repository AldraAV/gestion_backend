Flujo de usuario: Ciudadano abre sigras.mx (o el dominio que tenga)
        ↓
Selecciona “Reportar emergencia” o “Buscar ayuda”
        ↓
Autoriza ubicación o introduce municipio
        ↓
Selecciona tipo de necesidad
        ↓
Agrega descripción, foto o audio opcional
        ↓
Indica número de personas y vulnerabilidades
        ↓
Envía el reporte
        ↓
Recibe folio
        ↓
Consulta refugios, rutas o estado de atención

---[Determinar en la base de datos y adaptar según sea necesario. Español y datos concisos]

# Prompt: Endpoint de reportes ciudadanos anónimos con folio — SIGRAS

## Contexto
Stack: frontend Vite + React, backend FastAPI, base de datos Supabase (Postgres).
Es el flujo de "Reportar emergencia" de una plataforma de coordinación de protección civil (SIGRAS). El usuario que reporta (ciudadano afectado o en situación vulnerable) **no debe registrarse ni autenticarse** — el folio generado por el backend es su única credencial para dar seguimiento.

## Objetivo
Implementar la creación y consulta anónima de reportes:

1. **POST /api/reportes** — sin autenticación.
   - Recibe: `municipio`, `tipo_necesidad`, `descripcion` (opcional), `lat`/`lng` (opcional), `num_personas`, `personas_vulnerables` (bool), `foto_path`/`audio_path` (opcional, referencias a Supabase Storage, no archivos binarios).
   - Genera un folio único, legible por teléfono, con formato `SIGRAS-XXXXXX` usando un alfabeto sin caracteres ambiguos (sin 0/O, 1/I/l).
   - Guarda el reporte con estatus inicial `"recibido"`.
   - Devuelve `{ "folio": "..." }`.

2. **GET /api/reportes/{folio}** — sin autenticación.
   - El folio es la única prueba de identidad necesaria.
   - Devuelve **solo** `folio`, `estatus` y `actualizado` — nunca la descripción completa, ubicación exacta ni datos personales, por minimización de datos (LFPDPPP).
   - 404 si el folio no existe.

## Requisitos de anti-abuso (sin fricción para el usuario real)
- **Nada de CAPTCHA en el submit** — durante una emergencia real el pico de reportes legítimos es alto y no se puede frenar.
- **Honeypot field**: un campo oculto por CSS en el formulario; si llega lleno en el POST, responder con un folio falso (200 OK) pero no persistir el reporte — así el bot no sabe que fue detectado.
- **Rate limit por IP** (no por usuario, porque no hay usuario) usando `slowapi`, algo como 5 reportes/minuto por IP. En memoria basta para el alcance del hackathon, no se necesita Redis todavía.

## Manejo de fotos/audio
No subir binarios directo a FastAPI. Flujo: el frontend pide una URL firmada de subida al backend → sube el archivo directo a Supabase Storage → el POST del reporte solo lleva el `path` de referencia, no el archivo.

## Frontend
- Al recibir el folio, mostrarlo en pantalla de forma prominente (tamaño grande, opción de copiar) porque el ciudadano puede consultar desde otro dispositivo o un familiar puede hacerlo por él.
- Guardarlo también en `localStorage` como conveniencia para autocompletar si vuelve desde el mismo dispositivo — esto es solo UX, no es el mecanismo de seguridad.

## Explícitamente fuera de alcance (no implementar, solo dejar comentado o en un TODO)
- Modo offline con sincronización posterior (PWA + service workers) — es trabajo real de otra magnitud, se reconoce como brecha conocida, no se resuelve en este sprint.

## Entregable esperado
Código de los dos endpoints en FastAPI (con SQLModel), el rate limiter configurado, la función `generar_folio()`, y el snippet de React para el submit + guardado en localStorage. Todo en español (nombres de variables, funciones, comentarios), consistente con el estándar de nomenclatura del equipo.

