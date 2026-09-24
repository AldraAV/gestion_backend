# SIGRAS — Integración de Fuentes de Datos de Clima y Desastres Naturales
Equipo TLAMATI-ITSNA · HackaTec Regional 2026

---

## 1. Resumen de fuentes

| Fuente | Qué da | Auth | Costo | Prioridad |
|---|---|---|---|---|
| CONAGUA / SMN | Pronóstico por municipio (día/3 días, hora/48h) + estaciones hidrológicas (SIH) + mapas de inundación + RSS de ciclones | Ninguna (servicio público) | Gratuito | **1 — oficial, satisface el Reglamento (Art. 22-III)** |
| USGS Earthquake API | Sismos en tiempo casi real, magnitud, epicentro, profundidad | Ninguna | Gratuito | **1 — sismos** |
| NASA FIRMS | Anomalías térmicas / incendios vía satélite | API key gratuita (registro) | Gratuito | 2 — riesgo de incendio |
| GDACS | Agregador global de desastres (RSS + API) | Ninguna | Gratuito | 3 — respaldo/cruce |
| Open-Meteo | Clima genérico, JSON limpio | Ninguna | Gratuito | 3 — fallback de desarrollo, NO para el pitch final |

---

## 2. Patrón de integración — abstracción, no acoplamiento directo

Mismo principio que ya se definió para `ServicioRutas`: cada fuente externa se esconde detrás de una interfaz propia. Ningún controlador de SIGRAS debe llamar directamente a `requests.get("https://api.usgs.gov/...")` — todo pasa por un adaptador.

```
ProveedorClima (interfaz)
  ├── ProveedorClimaConagua   (producción — cumple Reglamento)
  └── ProveedorClimaOpenMeteo (fallback de desarrollo)

ProveedorSismos (interfaz)
  └── ProveedorSismosUSGS

ProveedorIncendios (interfaz)
  └── ProveedorIncendiosFIRMS

ProveedorDesastresGlobal (interfaz)
  └── ProveedorDesastresGDACS
```

**Por qué esto importa para el pitch, no solo para el código:** les permite decir ante el jurado "en producción usamos la fuente oficial del Estado mexicano" sin haber bloqueado el desarrollo mientras conseguían acceso completo al web service de CONAGUA — desarrollan contra Open-Meteo, cambian una sola clase al final.

Cada adaptador expone el mismo contrato hacia el resto del sistema — un método que recibe coordenadas o un municipio y devuelve un objeto normalizado ya traducido a los nombres de campo en español que usa SIGRAS (`temperatura`, `precipitacion_mm`, `viento_kmh`), sin importar cómo cada proveedor externo nombre sus campos.

**Flujo hacia las tablas ya definidas:**
- Un job programado (ver sección 5) consulta cada proveedor periódicamente.
- Si un dato cruza un umbral (ej. precipitación acumulada > X mm en Y horas, sismo > magnitud Z), el sistema genera automáticamente una entrada candidata en `zonas_riesgo` con `activa = true` y un `expira_en` calculado.
- Esa generación automática queda registrada en `acciones_ia` si pasó por el Coordinador vía tool_calling, o en un log aparte (`ingestas_externas`) si fue puramente mecánico sin intervención de IA — no mezclar ambos, porque el jurado va a preguntar cuál decisión fue de la IA y cuál fue una regla fija.

---

## 3. Detalle por fuente

### 3.1 CONAGUA / SMN — clima oficial

- **Acceso:** `smn.conagua.gob.mx/es/web-service-api` — el endpoint exacto hay que copiarlo desde ahí en navegador (el sitio bloquea scraping automatizado de su página de documentación, pero el servicio en sí es de consumo libre).
- **Formato:** JSON comprimido, se descomprime al recibir.
- **Frecuencia de actualización de la fuente:** cada hora y 15 minutos.
- **Granularidad:** por municipio — encaja directo con el campo `municipio` que ya tienen en `reportes` y `albergues`.
- **Datos abiertos complementarios:** `historico.datos.gob.mx/busca/organization/conagua` — mapas de peligro por inundación (retorno de 100 años, NOM-011-CONAGUA-2015), estaciones del SIH (viento, temperatura, precipitación cada ~10 min), RSS de avisos de ciclón tropical.
- **Mapea a:** `zonas_riesgo` (polígonos de inundación), campos de clima de apoyo en el dashboard del Coordinador.

### 3.2 USGS Earthquake API — sismos

- **Por qué esta y no una fuente mexicana:** el Servicio Sismológico Nacional (SSN-UNAM) publica un catálogo histórico descargable pero no una API REST pública para consumo en vivo. USGS sí, es gratuita, sin llave, y cubre territorio mexicano con buena latencia.
- **Formato:** GeoJSON — geometría lista para pintar directo en el mapa (MapLibre), sin transformar.
- **Filtros útiles:** magnitud mínima, bounding box (puedes acotar a Veracruz), ventana de tiempo.
- **Mapea a:** `incidencias` (tipo = sismo) generadas automáticamente cuando la magnitud supera el umbral que definan.

### 3.3 NASA FIRMS — incendios

- **Requiere:** registro gratuito para obtener API key (no es de pago, solo identificación).
- **Formato:** CSV o JSON según endpoint, coordenadas de anomalías térmicas detectadas por satélite (MODIS/VIIRS).
- **Mapea a:** `zonas_riesgo` (tipo = incendio) — útil sobre todo si el alcance del piloto incluye zonas serranas o forestales, no solo la cuenca de los ríos que motivó el proyecto.

### 3.4 GDACS — respaldo/cruce

- **Uso recomendado:** no como fuente primaria, sino como segunda opinión — si CONAGUA está caída o lenta en pleno pico de emergencia real, GDACS te da una señal de que algo está pasando a nivel nacional/regional sin depender de un solo proveedor.

### 3.5 Open-Meteo — fallback de desarrollo

- **Uso recomendado:** solo mientras desarrollan, nunca en el documento final del pitch como fuente de producción. Free, sin llave, JSON limpio — permite avanzar el `ProveedorClima` sin esperar acceso completo al web service de CONAGUA.

---

## 4. Dependencias a instalar (Python / FastAPI)

```bash
pip install httpx           # cliente HTTP async — todas las llamadas a proveedores externos van aquí, no con requests (bloqueante)
pip install pydantic        # modelos de validación de las respuestas normalizadas de cada ProveedorX
pip install apscheduler     # o rq/celery si ya tienen worker; para el job periódico de ingesta
pip install shapely         # operaciones geométricas (intersección de sismo/inundación con zonas_riesgo existentes)
pip install geojson-pydantic  # validar/tipar las respuestas GeoJSON del USGS antes de guardarlas
```

Ya tenían en su stack: `pgvector` en Supabase — para esto no lo necesitan, lo que sí conviene activar en la misma instancia de Postgres es **PostGIS** (ya mencionado en el documento de arquitectura anterior) para guardar y consultar las geometrías que lleguen de CONAGUA/USGS/FIRMS.

## 5. Variables de entorno

```
CONAGUA_SMN_BASE_URL=
USGS_EARTHQUAKE_BASE_URL=https://earthquake.usgs.gov/fdsnws/event/1/query
FIRMS_API_KEY=
GDACS_FEED_URL=
CLIMA_PROVIDER=conagua   # o "openmeteo" en ambiente de desarrollo — así el equipo cambia de fuente sin tocar código
```

## 6. Programación de la ingesta

- **Clima (CONAGUA):** cada 1 hora es suficiente — la fuente misma se actualiza cada hora y 15 min, consultar más seguido no aporta nada.
- **Sismos (USGS):** cada 1–5 minutos — un sismo es información que pierde valor rápido.
- **Incendios (FIRMS):** cada 3–6 horas — los satélites que alimentan FIRMS no pasan más seguido que eso sobre una misma zona.
- **GDACS:** cada 6 horas, es solo respaldo.

No metan los cuatro jobs en el mismo proceso del API principal de FastAPI — un scheduler separado (APScheduler en un proceso aparte, o un worker) evita que una fuente externa lenta o caída bloquee las peticiones de los usuarios reales.
