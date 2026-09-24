# INFORME EJECUTIVO INTEGRAL DE ARQUITECTURA Y ESTADO DEL PROYECTO
## PROYECTO: SIGRAS — Sistema Inteligente de Gestion de Rutas y Alertas Seguras
### DESTINATARIO: Claude (Mano Derecha de Ingenieria / Arquitectura de Software)
### EMISOR: Co-Ingeniero de Software y Arquitectura de Sistemas (HackaTec Regional 2026)
### FECHA DE CORTE: Septiembre 2026
### AMBITO: SaaS B2G para Proteccion Civil y Gestion Integral del Riesgo de Desastres

---

## 1. VISION GENERAL DEL SOFTWARE Y PROPOSITO DEL SISTEMA

### 1.1 Que es SIGRAS
**SIGRAS** (Sistema Inteligente de Gestion de Rutas y Alertas Seguras para la poblacion civil) es una plataforma digital GovTech bajo modelo B2G (Business-to-Government), concebida para dotar a las instituciones de Proteccion Civil municipales, estatales y federales de una **capacidad unificada de comando, visibilidad territorial y respuesta operativa ante contingencias hidrometeorologicas**.

El sistema atiende la problematica historica de desastres naturales en Mexico (evidenciada en contingencias como las inundaciones en el norte de Veracruz —Poza Rica, Alamo, Panuco— y la zona conurbada del sur de Tamaulipas —Tampico, Ciudad Madero, Altamira—), caracterizada por:
1. Fragmentacion de la informacion critica en tiempo real.
2. Saturacion de lineas de emergencia convencionales.
3. Descoordinacion entre refugios temporales, centros de acopio y brigadas en terreno.
4. Falta de canales directos que proporcionen a los ciudadanos rutas de escape que eviten vialidades inundadas o deslaves.

### 1.2 Las Dos Capas de Interaccion de la Plataforma
1. **Capa Civil (Usuario Final Sensible):**
   * Interfaz publica, ultra-ligera y accesible que no requiere autenticacion ni descarga de aplicaciones nativas.
   * Proporciona geolocalizacion instantanea, catalogo visual de albergues abiertos con semaforo de capacidad, centros de acopio y trazo de rutas vehiculares seguras evadiendo zonas de riesgo.
   * Modulo de reporte ciudadano para alertar sobre emergencias (inundaciones, personas atrapadas, arboles caidos) generando un folio unico de seguimiento.
2. **Capa Administrativa (Proteccion Civil y Sala de Crisis):**
   * Consola de mando para directores de Proteccion Civil, administradores de albergues y jefes de brigada.
   * Monitoreo en tiempo real de ocupacion de albergues, inventario consolidado de suministros, validacion de reportes ciudadanos y emision de alertas meteorologicas.

---

## 2. ARQUITECTURA TECNOLOGICA Y STACK EN PRODUCCION

```
[ NAVEGADOR CIUDADANO / MOVIL ]          [ DASHBOARD ADMINISTRATIVO ]
               │                                      │
               ▼                                      ▼
    [ TUNEL SEGURO CLOUDFLARE ] (Edge Anycast QUIC / HTTP/2)
               │
               ▼
   [ SERVIDOR FASTAPI (PYTHON 3.11.5) ]
   ├── Middleware de Auditoria CORS Universal y Normalizacion de Rutas
   ├── Router Publico (/api/v1/publico/...)
   ├── Router de Autenticacion (/api/v1/login/...)
   └── Adaptador Geoespacial (Mapbox Directions API v5)
               │
               ▼
   [ POSTGRESQL EN SUPABASE ]
   ├── 11 Tablas Fisicas Normalizadas
   ├── Claves Foraneas e Integridad Referencial
   └── Cifrado de Contrasenas con Argon2
```

* **Backend:** FastAPI estructurado con SQLModel y SQLAlchemy, corriendo sobre Python 3.11.5 gestionado hermeticamente mediante `uv`.
* **Base de Datos:** PostgreSQL administrado en Supabase, con 11 tablas fisicas, claves foraneas activas y soporte geoespacial.
* **Seguridad y Criptografia:** Cifrado de contrasenas mediante **Argon2** (`passlib[argon2]`), autenticacion OAuth2 Password Flow y emision de tokens Bearer JWT (`pyjwt`).
* **Proveedor de Mapas y Ruteo:** Mapbox Directions API v5 y tiles vectoriales interactivos.
* **Exposicion y Conectividad Externa:** Tunel seguro de Cloudflare (`cloudflared.exe`) que permite exponer el backend local hacia dispositivos moviles y clientes frontend en `http://localhost:3000` con SSL/TLS automatico.

---

## 3. JERARQUIA DETERMINISTA DE ROLES (6 NIVELES DE PRIVILEGIO)

De acuerdo con la especificacion arquitectonica del proyecto (`SIGRAS_Arquitectura_Roles_API.md`), la gobernanza de accesos se estructura en 6 niveles:

| Nivel | Rol Oficial | Ambito / Alcance | Privilegios Principales |
| :---: | :--- | :--- | :--- |
| **1** | **Usuario Final Sensible** | Publico (Sin autenticacion) | Visualizar mapa, consultar albergues y centros de acopio, solicitar ruta segura evitando riesgos, emitir reporte ciudadano sin registro y consultar estatus por folio. |
| **2** | **Persona Albergada** | Registro operativo interno | No posee credencial de acceso; su registro y transicion de estados (`ingresado`, `en_albergue`, `egresado`, `trasladado`) es gestionado exclusivamente por el personal del albergue. |
| **3** | **Coordinador de Emergencias** | Mando General / Sala de Crisis | Acceso total al backend, validacion de reportes ciudadanos, declaracion de alertas y zonas de riesgo, despacho de brigadas y uso exclusivo de la IA mediante Tool Calling. |
| **4** | **Administrador de Albergue** | 1 Albergue Especifico | Control de aforo, actualizacion de inventarios de viveres e infraestructura, asignacion de dormitorios y control nominal de personas refugiadas. |
| **5** | **Responsable de Area** | 1 Area Funcional (Salud, Cocina, etc.) | Gestion de insumos de su area (medicamentos, raciones de comida), solicitud de requerimientos urgentes y pase de lista de su personal. |
| **6** | **Personal Operativo** | Tareas de campo y comisiones | Registro de incidencias en sitio, captura de datos en triaje de puerta y asistencia directa en atencion de damnificados. |

---

## 4. INVENTARIO COMPLETO DE ENDPOINTS Y ESTADO DE DISPONIBILIDAD

### 4.1 Endpoints Activos y Verificados al 100%

#### A. Autenticacion Administrativa:
* `POST /api/v1/login/access-token`
  - **Estatus:** Operativo (`200 OK`).
  - **Formato:** `OAuth2PasswordRequestForm` (`username`, `password`).
  - **Superusuario Oficial Verificado:** `admin@proteccioncivil.gob.mx` | Password: `Admin1234!`
  - **Respuesta:** Bearer Token JWT (`access_token`, `token_type: "bearer"`).

#### B. Capa Publica (Usuario Final Sensible):
* `GET /api/v1/publico/ubicaciones`
  - **Estatus:** Operativo (`200 OK`).
  - **Proposito:** Entrega inmediata de la totalidad de pines para renderizar capas en Leaflet / Mapbox.
  - **Datos que retorna:**
    1. Albergues habilitados con capacidad total y cupo disponible (ej. Polideportivo Oriente, Col. San Lucas).
    2. Centros de acopio de viveres (ej. Plaza de Armas).
    3. Bloqueos viales y calles anegadas por inundacion (ej. Av. Moctezuma con 65 cm de agua, Calle Tampico).
* `POST /api/v1/publico/rutas/segura` y `GET /api/v1/publico/rutas/segura`
  - **Estatus:** Operativo (`200 OK`).
  - **Proposito:** La **Funcion Estrella** del sistema.
  - **Payload de Entrada:**
    ```json
    {
      "siteId": "cc-centro",
      "latitude": 22.2548,
      "longitude": -97.8487
    }
    ```
  - **Procesamiento:** Intercepta la ubicacion de salida, resuelve las coordenadas del destino, evalua las zonas de riesgo hidrometeorologico activas, inyecta exclusiones geodeticas en Mapbox Directions y retorna la polilinea segura GeoJSON con distancia (metros) y duracion (segundos).

### 4.2 Endpoints Disenados y Proyectados para la Fase 2

* **Reportes Ciudadanos:**
  - `POST /api/v1/publico/reportes`: Generacion de ticket ciudadano georreferenciado con folio unico.
  - `GET /api/v1/publico/reportes/{folio}`: Consulta publica anonima del avance del reporte.
* **Gestion de Sala de Crisis (Coordinador):**
  - `GET /api/v1/admin/reportes`: Bandeja de entrada de incidentes para triaje de Proteccion Civil.
  - `POST /api/v1/admin/incidencias/{id}/validar`: Promocion de reporte a incidencia oficial.
  - `POST /api/v1/admin/zonas-riesgo`: Creacion manual o asistida por IA de poligonos de peligro.
  - `POST /api/v1/admin/ia/accion-mapa`: Ejecucion de Tool Calling de IA sobre el mapa.
* **Operacion de Refugios:**
  - `GET /api/v1/admin/albergues/{id}/personas`: Censo de damnificados en sitio.
  - `PATCH /api/v1/admin/albergues/{id}/personas/{persona_id}/estado`: Transicion de estancia.
  - `PATCH /api/v1/admin/albergues/{id}/capacidad`: Actualizacion instantanea de aforo.

---

## 5. DESGLOSE DE LAS 'FUNCIONES' MATRICIALES DEL SISTEMA

### 5.1 La 'Funcion Estrella': Calculo y Navegacion Segura Evadiendo Riesgos
* **Modulo Responsable:** `backend/app/api/routes/rutas_seguras.py`.
* **Mecanica Operativa:**
  1. **Captura Geoespacial:** Recibe latitud y longitud del GPS civil junto con el identificador del destino (`siteId` o coordenadas manuales).
  2. **Resolucion de Destino:** Busca en el catalogo oficial si el destino es un albergue o centro de acopio registrado (ej. `sh-polideportivo`, `sh-san-lucas`, `cc-centro`).
  3. **Evaluacion de Puntos de Peligro:** Consulta las alertas activas de nivel naranja/rojo en la base de datos (actualmente los cortes viales de Av. Moctezuma y Calle Tampico).
  4. **Inyeccion de Restricciones Geodeticas:** Construye el llamado a Mapbox Directions API con parametros de exclusion (`exclude=point(lon,lat)`), obligando al motor de enrutamiento a rodear la zona de agua y trazar una ruta transitable.
  5. **Resiliencia de Entrada:** Soporta metodos POST y GET, tolera trailing slashes (`/segura/`), decodifica parametros con comillas escapadas accidentales (`%27` o `'`), y provee salvaguarda lineal si el proveedor de mapas presenta intermitencia.

### 5.2 Funcion de Semafrizacion Dinamica de Albergues
* Mantenimiento de contadores independientes en la tabla `albergue`: `capacidad_total` y `capacidad_disponible`.
* Clasificacion visual instantanea para el mapa:
  - **Verde (`Abierto`):** Mas del 25% de plazas disponibles.
  - **Ambar (`Casi lleno`):** Menos del 25% de cupo restante.
  - **Rojo (`Lleno`):** 0 plazas disponibles. Redireccion automatica en puerta hacia el refugio alternativo mas proximo.

### 5.3 Funcion de Saneamiento y Normalizacion de Usuarios
* Modelo de compatibilidad hacia atras que preserva la tabla fisica original `"user"` para proteger las claves foraneas vinculadas.
* Incorporacion de campos operacionales (`rol` y `alcance_id`).
* Explotacion de `@property` en espanol en el modelo SQLModel (`correo`, `nombre`, `hash_password`, `creado_en`) para cumplir con la soberania de lenguaje sin alterar el motor fisico de PostgreSQL.

---

## 6. BITACORA DE TESTS Y VALIDACIONES DE INGENIERIA EJECUTADOS

Durante la construccion e integracion del software se ejecutaron baterias de pruebas rigurosas, identificando anomalias criticas y aplicando soluciones definitivas:

### Test 1: Verificacion de Enrutamiento Hacia Centro de Acopio Plaza de Armas (`cc-centro`)
* **Archivo de Prueba:** `backend/scripts/probar_cc_centro.py`.
* **Condicion:** Peticion POST con coordenadas de origen en Ciudad Madero (`22.2548, -97.8487`) hacia Plaza de Armas (`22.2156, -97.8579`).
* **Resultado:** Exitoso (`200 OK`). Retorno de geometria GeoJSON valida, 6.7 km de trayectoria calculada y 13.5 minutos estimados evadiendo la zona de anegacion de Av. Moctezuma.

### Test 2: Diagnostico del Falso Positivo de CORS provocado por Cloudflare Quick Tunnels
* **Sintoma:** El navegador del frontend en `http://localhost:3000` reportaba error de CORS:
  `No 'Access-Control-Allow-Origin' header is present on the requested resource` y fallo de red.
* **Causa Raiz Identificada:** No se trataba de una mala configuracion del CORS en FastAPI. El tunel rapido gratuito de Cloudflare sufrio un micro-reinicio de stream QUIC/UDP por inactividad de 1 segundo, respondiendo con una pagina HTML de error `502 Bad Gateway`. Debido a que las paginas de error por defecto de Cloudflare no incluyen encabezados CORS de la aplicacion origen, el navegador reporto el fallo como una violacion de CORS en lugar de un error de infraestructura.
* **Solucion Aplicada:**
  1. Implementacion de un middleware de auditoria y cabeceras obligatorias en `backend/app/main.py` que fuerza las cabeceras `Access-Control-Allow-Origin: *`, `Access-Control-Allow-Methods: *` y `Access-Control-Allow-Headers: *` en absolutamente todas las respuestas del servidor.
  2. Configuracion de keep-alive en transporte HTTP/1.1 para estabilizar el socket del tunel.

### Test 3: Saneamiento y Re-indexacion de la Tabla de Usuarios
* **Archivo de Prueba:** `backend/scripts/sanear_usuarios.py`.
* **Condicion:** Conflicto generado por scripts previos que intentaban forzar la tabla `usuarios_admin` y campos `correo`, rompiendo las claves foraneas de PostgreSQL.
* **Solucion:** Saneamiento quirurgico de `"user"`, agregando las columnas `rol` y `alcance_id` sin tocar las tablas dependientes. Inicializacion de `admin@proteccioncivil.gob.mx` con hash Argon2 verificado.
* **Resultado:** `POST /api/v1/login/access-token` devuelve `200 OK` y emite el token JWT valido.

### Test 4: Resolucion del Error de Generics en SQLModel con Python 3.10+
* **Sintoma:** Fallo catastrofico en el mapper de SQLAlchemy: `expression "relationship("list['Item']")" seems to be using a generic class`.
* **Causa Raiz:** La presencia de `from __future__ import annotations` convertia las definiciones de tipo en strings literales genericos en tiempo de carga.
* **Solucion:** Retiro estricto de `from __future__ import annotations` en todos los modelos de `backend/app/models/` (`usuario.py`, `item.py`, `albergue.py`, `albergue_usuario.py`).

### Test 5: Inspeccion Fisica Integral de la Base de Datos
* **Archivo de Prueba:** `backend/scripts/inspeccionar_esquema.py` y `backend/scripts/generar_doc_esquema.py`.
* **Resultado:** Extraccion automatica y parseo completo de las 11 tablas fisicas, volcadas en el documento de arquitectura [ESTRUCTURA_TABLAS_BASE_DE_DATOS.md](file:///c:/Users/carde/Desktop/MUACK_2.0/ESTRUCTURA_TABLAS_BASE_DE_DATOS.md).

---

## 7. IDEAS TENTATIVAS FORMALIZADAS (DOCUMENTADAS EN EL PROYECTO)

> **Nota de Fidelidad:** Las siguientes ideas provienen exclusivamente de los documentos de diseno del repositorio (`BRIEF_FUNDACIONAL.md`, `función_estrella.md`, `SIGRAS_Arquitectura_Roles_API.md`, `SIGRAS.md`, `SIGRAS2.md`, `SIGRAS3.md`, `SIGRAS4.md`) y representan la hoja de ruta pactada.

### Idea 1: Sala de Crisis con IA Geoespacial mediante Tool Calling
* **Documentos Fuente:** `BRIEF_FUNDACIONAL.md`, `función_estrella.md`, `SIGRAS_Arquitectura_Roles_API.md`.
* **Concepto:** Integrar un modelo LLM con alta velocidad de inferencia y soporte nativo de Tool Calling (Llama 3 en Groq, Gemini Flash, Cohere Command R+, Mistral) que asista al Coordinador de Emergencias.
* **Capacidades Tentativas:**
  1. Interpretacion de lenguaje natural para delimitar poligonos de riesgo ("Dibuja zona de desbordamiento en la Laguna del Carpintero con radio de 500 metros").
  2. Ajuste dinamico de capas en Mapbox mediante herramientas (`tools`) registradas en el backend.
  3. Registro inmutable en la tabla proyectada `acciones_ia` para auditar que comando se ejecuto, quien lo autorizo y que modifico en la cartografia oficial.

### Idea 2: Alternativa Tecnologica a Mapbox (MapLibre GL JS + OpenRouteService + PostGIS)
* **Documento Fuente:** `SIGRAS_Arquitectura_Roles_API.md` (Seccion 6).
* **Fundamento Tecnico:** Mapbox Directions API solo admite exclusion de puntos aislados (`exclude=point(lon,lat)`, maximo 50 puntos). No cuenta con exclusion nativa de poligonos geometricos de inundacion.
* **Ruta Tentativa Propuesta:**
  1. **Visualizacion:** Migrar a **MapLibre GL JS** (fork de codigo abierto, sin cobros por vistas de mapa, compatible con tiles OpenStreetMap o MapTiler).
  2. **Ruteo con Poligonos:** Usar **OpenRouteService (ORS)** que soporta nativamente el parametro `avoid_polygons`.
  3. **Base de Datos Espacial:** Activar la extension **PostGIS** en Supabase para ejecutar calculos de proximidad (`ST_Distance`, `ST_DWithin`) directo en el motor de la base de datos en vez de procesar matrices en memoria de Python.

### Idea 3: Modelo de Negocio GovTech B2G con Facturacion Recurrente
* **Documentos Fuente:** `SIGRAS.md`, `SIGRAS2.md`, `SIGRAS3.md`, `SIGRAS4.md`.
* **Fundamento:** Queda descartada una licencia vitalicia. Los costos de APIs de mapas, tokens de IA, almacenamiento de evidencia multimedia y hosting de base de datos son continuos.
* **Esquema Tentativo:**
  1. **Cobro Unico de Implementacion:** Diagnostico de la red municipal/estatal de Proteccion Civil, parametrizacion territorial, carga de albergues y capacitacion de brigadas.
  2. **Suscripcion Recurrente (Anual/Mensual):** Mantenimiento de servidores, licencias de APIs geoespaciales, bolsa de tokens de IA para la Sala de Crisis y soporte 24/7 en temporada de huracanes.
  3. **Expansion:** Piloto inicial en la zona conurbada de Tamaulipas / Norte de Veracruz con escalamiento hacia el Programa Nacional de Proteccion Civil.

### Idea 4: Trazabilidad Medica y Legal de Refugiados (`historial_estados_persona`)
* **Documento Fuente:** `SIGRAS_Arquitectura_Roles_API.md`.
* **Concepto:** En situaciones de desastre, los datos de personas vulnerables requieren cadena de custodia estricta. Implementar la tabla de auditoria `historial_estados_persona` para registrar el identificador del brigadista, la estampa de tiempo y el motivo de cada traslado o egreso.

### Idea 5: Prevencion de Condiciones de Carrera en la Capacidad de Refugios
* **Documento Fuente:** `SIGRAS_Arquitectura_Roles_API.md`.
* **Concepto:** Durante una evacuacion masiva en la noche de la tormenta, cientos de personas llegan a los refugios en minutos. Se prohibe calcular la disponibilidad restando dinamicamente en cada peticion (`COUNT(refugiados)`); en su lugar, se actualiza un contador atomico con bloqueos transaccionales en PostgreSQL (`SELECT FOR UPDATE`) para evitar sobrecupo en albergues criticos.

---

## 8. RESUMEN DE AMBIENTE OPERATIVO PARA CLAUDE

Si Claude o cualquier agente de ingenieria necesita interactuar o verificar el entorno:
* **Directorio Backend:** `C:\Users\carde\Desktop\HACKATEC_proyecto\backend`
* **Directorio Frontend:** `C:\Users\carde\Desktop\HACKATEC_proyecto\Frontend`
* **Arranque Servidor FastAPI:**
  ```powershell
  & "C:\Program Files\PowerShell\7\pwsh.exe" -Command "cd C:\Users\carde\Desktop\HACKATEC_proyecto\backend; uv run uvicorn app.main:app --host 0.0.0.0 --port 8000"
  ```
* **Arranque Tunel Cloudflare:**
  ```powershell
  & "C:\Program Files\PowerShell\7\pwsh.exe" -Command "cd C:\Users\carde\Desktop\HACKATEC_proyecto\backend; .\cloudflared.exe tunnel --url http://127.0.0.1:8000"
  ```
* **Tunel Activo Actual:** `https://buddy-week-great-flip.trycloudflare.com`
* **Credenciales Superusuario:** `admin@proteccioncivil.gob.mx` | `Admin1234!`

---
*Informe generado para Claude con apego total a la arquitectura y antecedentes reales de SIGRAS.*
