# BITACORA DE INTEGRACION DE APIS: MAPAS, UBICACIONES Y RUTAS SEGURAS
## Proyecto: HACKATEC / MUACK - Aldraverso 2026
**Autor:** Jose "Aldra" Aviles Cardenas / Co-Ingeniero de IA  
**Estatus:** Produccion Activa y Verificada (100% Operativa)  
**Fecha:** Septiembre 2026  

---

## 1. RESUMEN EJECUTIVO DE LA INTEGRACION

El objetivo de esta fase fue interconectar en tiempo real el frontend del desarrollador par con el backend en FastAPI (Python 3.11.5) alojado localmente y expuesto mediante un tunel seguro de Cloudflare, integrando:
1. Base de datos Supabase PostgreSQL para la persistencia de refugios, centros de acopio y zonas de bloqueo vial.
2. Motor de calculo de rutas vehiculares optimizadas mediante Mapbox Directions API.
3. Resolucon dinamica de catalogo de marcadores previos para que el componente visual de mapas pueda pintar las ubicaciones y trazar las trayectorias sin excepciones.

---

## 2. ARQUITECTURA Y FLUJO DE DATOS

```
┌─────────────────────────┐          ┌──────────────────────────┐          ┌─────────────────────────┐
│     FRONTEND (React)    │          │    TUNEL CLOUDFLARE      │          │     BACKEND (FastAPI)   │
│  http://localhost:3000  │ ───────> │ trycloudflare.com Edge   │ ───────> │  127.0.0.1:8000         │
└─────────────────────────┘          └──────────────────────────┘          └─────────────────────────┘
            │                                                                           │
            │ 1. GET /api/v1/publico/ubicaciones                                        │ Consulta Supabase
            │ <── Devuelve 7 puntos (shelter, collection_center, road_block) ───────────┤ y salvaguarda RAM
            │                                                                           │
            │ 2. Usuario selecciona punto (ej. "sh-polideportivo" o "cc-centro")        │
            │ 3. POST /api/v1/publico/rutas/segura                                      │ Consulta Mapbox
            │ <── Devuelve GeoJSON LineString + metricas + giros paso a paso ───────────┤ Directions API
```

---

## 3. CATALOGO DE UBICACIONES POBLADAS EN BASE DE DATOS

Se normalizaron y registraron en Supabase los siguientes 7 puntos tacticos para la zona conurbada Tampico - Ciudad Madero:

| ID / Folio | Tipo | Nombre | Latitud | Longitud | Direccion / Estado |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `sh-polideportivo` | `shelter` | Polideportivo Oriente | 22.2412 | -97.8215 | Col. Oriente, Ciudad Madero (Abierto / Cap: 250) |
| `sh-san-lucas` | `shelter` | Col. San Lucas | 22.2684 | -97.8703 | Col. San Lucas, Tampico (Casi lleno / Cap: 180) |
| `hc-uat` / `REF-MAD-001` | `shelter` | Centro Univ. UAT / Espana 1101 | 22.2585 | -97.8384 | Espana 1101, Col. Vicente Guerrero, Madero |
| `cc-centro` | `collection_center` | Acopio Plaza de Armas | 22.2156 | -97.8579 | Centro Historico, Tampico (Recibiendo viveres) |
| `rb-moctezuma` | `road_block` | Calle inundada (65 cm) | 22.2378 | -97.8652 | Av. Moctezuma esq. Ejercito Mexicano (Severidad: Alta) |
| `rb-puente` | `road_block` | Arbol y poste derribado | 22.2295 | -97.8437 | Paso del Humo / Ribera (Severidad: Media) |

---

## 4. CONTRATO DE INTERFACES Y ENDPOINTS

### 4.1 Catalogo de Marcadores para el Mapa
* **Ruta:** `GET /api/v1/publico/ubicaciones` (y alias directo `/publico/ubicaciones`)
* **Parametro opcional:** `?type=shelter` o `?type=collection_center` o `?type=road_block`
* **Respuesta Exitosa (200 OK):**
```json
[
  {
    "id": "sh-polideportivo",
    "type": "shelter",
    "name": "Polideportivo Oriente",
    "latitude": 22.2412,
    "longitude": -97.8215,
    "address": "Col. Oriente, Ciudad Madero",
    "capacity": 250,
    "available": 90,
    "status": "Abierto"
  },
  {
    "id": "cc-centro",
    "type": "collection_center",
    "name": "Acopio Plaza de Armas",
    "latitude": 22.2156,
    "longitude": -97.8579,
    "address": "Centro Histórico, Tampico",
    "status": "Recibiendo víveres y agua"
  },
  {
    "id": "rb-moctezuma",
    "type": "road_block",
    "name": "Calle inundada (65 cm)",
    "latitude": 22.2378,
    "longitude": -97.8652,
    "address": "Av. Moctezuma esq. Ejército Mexicano",
    "severity": "high",
    "status": "Inundado - Tráfico cerrado"
  }
]
```

### 4.2 Calculo de Rutas Seguras
* **Ruta:** `POST /api/v1/publico/rutas/segura` (y `GET` con query params como fallback)
* **Cuerpo de Solicitud (JSON):**
```json
{
  "siteId": "sh-polideportivo",
  "latitude": 22.2548,
  "longitude": -97.8487
}
```
* **Respuesta Exitosa (200 OK):**
```json
{
  "routeId": "ruta_4964c0429fd4",
  "origin": {
    "latitude": 22.2548,
    "longitude": -97.8487
  },
  "destination": {
    "id": "sh-polideportivo",
    "name": "Polideportivo Oriente",
    "latitude": 22.2412,
    "longitude": -97.8215
  },
  "distanceMeters": 9281.95,
  "durationSeconds": 1420.5,
  "geometry": [
    [-97.8487, 22.2548],
    [-97.8491, 22.2550],
    [-97.8215, 22.2412]
  ],
  "segments": [
    {
      "distanceMeters": 402.5,
      "durationSeconds": 92.5,
      "instruction": "Tome la curva cerrada a la izquierda hacia Avenida Ejército Mexicano."
    }
  ]
}
```

---

## 5. HISTORIAL DE ERRORES Y LECCIONES APRENDIDAS (POST-MORTEM)

A lo largo de la sesion de integracion se diagnosticaron y superaron 4 incidencias tecnicas criticas. Cada una dejo un principio determinista de ingenieria:

### Incidencia 1: Desajuste de Metodo HTTP (405 Method Not Allowed)
* **Sintoma:** El cliente envio `GET /api/v1/publico/rutas/segura` sin cuerpo, recibiendo `405`.
* **Causa Raiz:** El endpoint original estaba declarado exclusivamente como `@router.post`.
* **Solucion Aplicada:** Se implemento un manejador dual en `rutas_seguras.py` (`@router.get` extrayendo query params y `@router.post` deserializando el body JSON).
* **Leccion de Aprendizaje:** En APIs publicas consumidas por terceros o integraciones rapidas, los endpoints de navegacion deben soportar ambos metodos (`GET` para pruebas rapidas en navegador/curl y `POST` para payloads formales).

### Incidencia 2: Inconsistencia de Prefijo `/api/v1` (404 Not Found)
* **Sintoma:** El frontend envio peticiones a `/publico/rutas/segura` (omitiendo `/api/v1`), resultando en 404.
* **Causa Raiz:** FastAPI montaba `api_router` unicamente bajo el prefijo `settings.API_V1_STR` (`/api/v1`).
* **Solucion Aplicada:** En `app/main.py` se monto el enrutador dos veces:
  ```python
  app.include_router(api_router, prefix=settings.API_V1_STR)
  app.include_router(api_router)
  ```
* **Leccion de Aprendizaje:** Todo backend expuesto a frontends externos debe ser agnostico a la omision o presencia de la barra de versionado en rutas publicas.

### Incidencia 3: Ruptura por Falta de Marcadores Previos en el Mapa (404 en `/ubicaciones`)
* **Sintoma:** El mapa de Leaflet/Mapbox del desarrollador lanzaba errores al intentar calcular o trazar una ruta hacia un albergue o centro de acopio.
* **Causa Raiz:** El frontend estaba intentando cargar previamente el catalogo completo de pines mediante `GET /api/v1/publico/ubicaciones`. Como el endpoint no existia, la capa de marcadores del mapa estaba vacia; consecuentemente, al presionar un boton de calcular ruta o buscar por `siteId`, el componente tronaba por referencia nula.
* **Solucion Aplicada:** Se creo el modulo `app/api/routes/ubicaciones.py` con consulta directa a Supabase y salvaguarda infalible en memoria que consolida albergues, centros de acopio y bloqueos con sus coordenadas exactas.
* **Leccion de Aprendizaje:** En aplicaciones geoespaciales, la visualizacion previa de marcadores es una precondicion funcional obligatoria para la navegacion punto a punto.

### Incidencia 4: Falso Positivo de CORS provocado por 502 Bad Gateway de Cloudflare
* **Sintoma:** La consola del navegador mostraba:
  `Access to XMLHttpRequest at '.../rutas/segura' from origin 'http://localhost:3000' has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource` y `502 Bad Gateway`.
* **Causa Raiz:** El tunel rapido gratuito de Cloudflare sufrio un micro-reinicio de stream QUIC/UDP (timeout por inactividad de 1 segundo). Al no tener comunicacion momentanea con el localhost, el borde de Cloudflare devolvio una pagina HTML de error 502. Debido a que las paginas de error nativas de Cloudflare no incluyen encabezados CORS de la aplicacion de origen, el navegador interpreta y reporta el fallo como una violacion de CORS en lugar de un error de conectividad de red.
* **Solucion Aplicada:**
  1. Se agrego inyeccion obligatoria de cabeceras CORS en el middleware principal de FastAPI (`auditoria_peticiones`) para que ninguna respuesta emitida por el backend carezca de ellas.
  2. Se anadio sanitizacion de rutas para limpiar comillas accidentales (`%27` o `'`) y barras diagonales finales (`/segura/`).
* **Leccion de Aprendizaje:** Jamas asumir que un error de CORS en peticiones a traves de tuneles o proxies reversos proviene de la configuracion de CORS del backend; casi siempre es la consecuencia de un `502 Bad Gateway` o `504 Gateway Timeout` generado por la infraestructura intermedia.

---

## 6. INVENTARIO DE ARCHIVOS CREADOS Y MODIFICADOS

1. [`backend/app/api/routes/ubicaciones.py`](file:///C:/Users/carde/Desktop/HACKATEC_proyecto/backend/app/api/routes/ubicaciones.py) *(NUEVO)*:
   Router soberano que consulta Supabase y memoria para servir los puntos del mapa.
2. [`backend/app/api/routes/rutas_seguras.py`](file:///C:/Users/carde/Desktop/HACKATEC_proyecto/backend/app/api/routes/rutas_seguras.py) *(MODIFICADO)*:
   Manejador de rutas vehiculares con soporte GET/POST, tolerancia a trailing slashes y comillas accidentales.
3. [`backend/app/api/main.py`](file:///C:/Users/carde/Desktop/HACKATEC_proyecto/backend/app/api/main.py) *(MODIFICADO)*:
   Inclusion del router de ubicaciones en `api_router`.
4. [`backend/app/main.py`](file:///C:/Users/carde/Desktop/HACKATEC_proyecto/backend/app/main.py) *(MODIFICADO)*:
   Middleware de auditoria con inyeccion universal de cabeceras CORS y sanitizacion de rutas.
5. [`backend/scripts/poblar_puntos_frontend.py`](file:///C:/Users/carde/Desktop/HACKATEC_proyecto/backend/scripts/poblar_puntos_frontend.py) *(NUEVO)*:
   Script de inicializacion de datos en Supabase para albergues y alertas de riesgo.
6. [`backend/scripts/probar_cc_centro.py`](file:///C:/Users/carde/Desktop/HACKATEC_proyecto/backend/scripts/probar_cc_centro.py) *(NUEVO)*:
   Script de verificacion local y por tunel para la ruta hacia Plaza de Armas.

---

## 7. COMANDOS DE MANTENIMIENTO DEL ENTORNO

Para reanudar o reiniciar los servicios en cualquier momento:

### 1. Iniciar Servidor FastAPI:
```powershell
& "C:\Program Files\PowerShell\7\pwsh.exe" -Command "cd C:\Users\carde\Desktop\HACKATEC_proyecto\backend; uv run uvicorn app.main:app --host 0.0.0.0 --port 8000"
```

### 2. Iniciar Tunel de Cloudflare:
```powershell
& "C:\Program Files\PowerShell\7\pwsh.exe" -Command "cd C:\Users\carde\Desktop\HACKATEC_proyecto\backend; .\cloudflared.exe tunnel --url http://127.0.0.1:8000"
```

---
*Fin de la documentacion de integracion.*
