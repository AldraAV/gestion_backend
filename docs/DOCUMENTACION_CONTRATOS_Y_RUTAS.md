# SISTEMA INTEGRAL DE GESTION DE REFUGIOS Y ALBERGUES (SIGRAS)
## ESPECIFICACION MAESTRA DE CONTRATOS, ENDPOINTS Y ARQUITECTURA DE RUTAS FRONTEND ↔ BACKEND

> **Estatus:** Documento Tecnico Oficial y Determinista  
> **Fecha:** 24 de Septiembre de 2026  
> **Ecosistema:** HackaTec 2026 / Proteccion Civil y Atencion de Emergencias  
> **Base URL Backend:** `http://127.0.0.1:8000/api/v1`

---

## 1. ARQUITECTURA DE DIVISION DE RUTAS EN FRONTEND

El sistema separa estrictamente dos perfiles de usuario con ciclos de vida independientes:

```
                                 [APLICACION WEB]
                                        │
           ┌────────────────────────────┴────────────────────────────┐
           ▼                                                         ▼
   [PERFIL CIUDADANO]                                     [PERFIL ADMINISTRATIVO]
   Rutas Publicas (Sin Login)                             Rutas Protegidas (Con Login)
   - Acceso universal inmediato                           - Autenticacion OAuth2 / Bearer JWT
   - Mapa interactivo de refugios                         - Protegido por Guardias de Ruta
   - Rutas de evacuacion seguras                          - Control de aforo e infraestructura
   - Centros de acopio y ayuda                            - Registro de ingreso familiar
   - Datos anonimizados (sin PII)                         - Carga masiva de inmuebles
```

### 1.1 Estructura de Rutas Frontend

| Ruta Frontend | Perfil | Proposito | Autenticacion Requerida |
| :--- | :--- | :--- | :--- |
| `/` o `/mapa` | Ciudadano | Mapa interactivo de refugios temporales y centros de acopio activos. | Publico (Ninguna) |
| `/ruta-segura` | Ciudadano | Asistente de navegacion y trazado de rutas de evacuacion evitando riesgos. | Publico (Ninguna) |
| `/albergues/:id` | Ciudadano | Ficha publica de un albergue (capacidad disponible, si admite mascotas, direccion). | Publico (Ninguna) |
| `/login` | Personal PC | Formulario de autenticacion oficial de brigadistas y coordinadores. | Publico |
| `/admin` | Personal PC | Redireccion inteligente segun rol operativo del usuario. | Requiere Token JWT |
| `/admin/dashboard` | Personal PC | Resumen general de albergues asignados, cupos, alertas criticas y suministros. | Requiere Token JWT |
| `/admin/albergues/:id/infraestructura` | Admin Albergue | Panel de control de las 9 areas fisicas con micro-ajustes atomicos en tiempo real. | Requiere Token JWT |
| `/admin/albergues/:id/ingreso-familiar` | Admin Albergue | Formulario de admision familiar inteligente con codigo de nucleo y prevencion de aforo. | Requiere Token JWT |
| `/admin/albergues/carga-masiva` | Coordinador PC | Importacion y georreferenciacion masiva de inmuebles y refugios temporales. | Requiere Rol Coordinador / Superadmin |

---

## 2. MECANISMO DE CONTROL DE ACCESO EN FRONTEND (GUARDS)

### 2.1 Guardia de Ruta para React (Ejemplo de Implementacion Limpia)

```typescript
// src/rutas/GuardiaRutaProtegida.tsx
import { ReactNode } from "react";
import { Navigate, useLocation } from "react-router-dom";
import { obtenerTokenAlmacenado, decodificarUsuario } from "@/servicios/autenticacion";

interface PropiedadesGuardia {
  children: ReactNode;
  rolRequerido?: string;
}

export const GuardiaRutaProtegida = ({ children, rolRequerido }: PropiedadesGuardia) => {
  const ubicacion = useLocation();
  const token = obtenerTokenAlmacenado();

  if (!token) {
    return <Navigate to="/login" state={{ desde: ubicacion }} replace />;
  }

  if (rolRequerido) {
    const usuario = decodificarUsuario(token);
    const esSuperusuario = usuario?.is_superuser === true;
    const tieneRol = usuario?.rol === rolRequerido;

    if (!esSuperusuario && !tieneRol) {
      return <Navigate to="/admin/dashboard" replace />;
    }
  }

  return <>{children}</>;
};
```

---

## 3. CONTRATOS FRONTEND ↔ BACKEND YA DEFINIDOS Y AUDITADOS

### 3.1 Contrato de Infraestructura

#### A. Obtener Estado de Infraestructura
- **Metodo:** `GET`
- **Ruta:** `/api/v1/albergues/{albergue_id}/infraestructura`
- **Autenticacion:** `Bearer <token>` (Superadmin, Coordinador de Emergencias o personal asignado al albergue).
- **Respuesta Exitosa (`200 OK`):**
```json
{
  "areas": [
    {
      "id": "dormitorios",
      "nombre": "Dormitorios",
      "cantidad": 4,
      "disponible": true,
      "subtitulo": "Espacios habilitados para pernocta"
    },
    {
      "id": "banos",
      "nombre": "Banos",
      "cantidad": 6,
      "disponible": true,
      "subtitulo": "Modulos sanitarios en servicio"
    },
    {
      "id": "regaderas",
      "nombre": "Regaderas",
      "cantidad": 4,
      "disponible": true,
      "subtitulo": "Zonas de aseo personal activas"
    },
    {
      "id": "cocina",
      "nombre": "Cocina",
      "cantidad": 1,
      "disponible": true,
      "subtitulo": "Espacio de preparacion de alimentos"
    },
    {
      "id": "comedor",
      "nombre": "Comedor",
      "cantidad": 1,
      "disponible": true,
      "subtitulo": "Capacidad de atencion por turnos"
    },
    {
      "id": "consultorio",
      "nombre": "Consultorio",
      "cantidad": 1,
      "disponible": true,
      "subtitulo": "Atencion medica primaria y triage"
    },
    {
      "id": "bodega",
      "nombre": "Bodega",
      "cantidad": 1,
      "disponible": true,
      "subtitulo": "Almacenamiento de suministros y donaciones"
    },
    {
      "id": "salidas_emergencia",
      "nombre": "Salidas de emergencia",
      "cantidad": 2,
      "disponible": true,
      "subtitulo": "Rutas de evacuacion despejadas"
    },
    {
      "id": "extintores_instalados",
      "nombre": "Extintores instalados",
      "cantidad": 4,
      "disponible": true,
      "subtitulo": "Equipos contra incendios verificados"
    }
  ],
  "fechaActualizacion": "2026-09-24T07:15:00.000Z"
}
```

#### B. Ajuste Atomico de Infraestructura
- **Metodo:** `POST`
- **Ruta:** `/api/v1/albergues/{albergue_id}/infraestructura/{areaId}/ajuste`
- **Autenticacion:** `Bearer <token>`
- **Payload (`application/json`):**
```json
{
  "delta": 1
}
```
*(Nota: `delta` puede ser positivo para incrementar o negativo para decrementar, ej. `-1`).*

- **Respuesta Exitosa (`200 OK`):**
```json
{
  "area": {
    "id": "dormitorios",
    "nombre": "Dormitorios",
    "cantidad": 5,
    "disponible": true,
    "subtitulo": "Espacios habilitados para pernocta"
  },
  "fechaActualizacion": "2026-09-24T07:15:30.000Z"
}
```

- **Respuestas de Error:**
  - `404 Not Found` (`{"error": "AREA_NO_ENCONTRADA", "mensaje": "..."}`): Area no pertenece a la lista blanca autorizada.
  - `422 Unprocessable Entity` (`{"error": "CANTIDAD_INVALIDA", "mensaje": "...", "area": {...}}`): El ajuste provocaria un conteo menor a cero, o `delta` es cero.
  - `403 Forbidden`: Usuario sin asignacion activa a dicho albergue.

---

### 3.2 Contrato de Ingreso Familiar Inteligente

- **Metodo:** `POST`
- **Ruta:** `/api/v1/albergues/{albergue_id}/ingreso-familiar`
- **Autenticacion:** `Bearer <token>`
- **Regla Determinista de Capacidad:** Opcion A (Bloque indivisible). Si el albergue no cuenta con cupo para la totalidad de los miembros del grupo, se rechaza la peticion completa con `409 Conflict` para garantizar la unidad familiar.
- **Payload (`application/json`):**
```json
{
  "nombre_grupo": "Familia Ramirez Hernandez",
  "contacto_telefono": "8331234567",
  "contacto_emergencia": "8339876543",
  "direccion_origen": "Calle Fco. I. Madero 102, Col. Miramar",
  "observaciones_grupo": "Evacuados por crecida de canal pluvial.",
  "personas": [
    {
      "nombre": "Juan",
      "apellido_paterno": "Ramirez",
      "apellido_materno": "Lopez",
      "edad": 42,
      "sexo": "M",
      "parentesco": "Jefe de familia",
      "curp": "RALJ840510HTSMNP01",
      "discapacidad": false,
      "embarazo": false,
      "observaciones_medicas": "Hipertension controlada"
    },
    {
      "nombre": "Maria",
      "apellido_paterno": "Hernandez",
      "apellido_materno": "Perez",
      "edad": 38,
      "sexo": "F",
      "parentesco": "Conyuge",
      "curp": "HEPM880315MTSLRR02",
      "discapacidad": false,
      "embarazo": false,
      "observaciones_medicas": null
    },
    {
      "nombre": "Mateo",
      "apellido_paterno": "Ramirez",
      "apellido_materno": "Hernandez",
      "edad": 7,
      "sexo": "M",
      "parentesco": "Hijo",
      "curp": null,
      "discapacidad": false,
      "embarazo": false,
      "observaciones_medicas": "Alergia a penicilina"
    }
  ]
}
```

- **Respuesta Exitosa (`201 Created`):**
```json
{
  "mensaje": "Ingreso familiar procesado exitosamente.",
  "grupo_familiar_id": "7ac96b93-f9a1-46ed-bc01-ae1ff758e5c5",
  "codigo_familia": "FAM-20260924-E8A1",
  "total_ingresados": 3,
  "ocupacion_actual_albergue": 18,
  "capacidad_maxima": 100,
  "cupo_remanente": 82,
  "personas_registradas": [
    {
      "id": "18f2d5e1-8842-4f32-8411-cf0193852101",
      "folio_refugiado": "REF-20260924-1001",
      "nombre_completo": "Juan Ramirez Lopez",
      "parentesco": "Jefe de familia",
      "es_vulnerable": false
    },
    {
      "id": "a901e4bc-7612-421e-9204-dc0817349182",
      "folio_refugiado": "REF-20260924-1002",
      "nombre_completo": "Maria Hernandez Perez",
      "parentesco": "Conyuge",
      "es_vulnerable": false
    },
    {
      "id": "b3109a12-8871-4209-9011-ea2190831093",
      "folio_refugiado": "REF-20260924-1003",
      "nombre_completo": "Mateo Ramirez Hernandez",
      "parentesco": "Hijo",
      "es_vulnerable": true
    }
  ]
}
```

- **Respuestas de Error:**
  - `409 Conflict`: Capacidad insuficiente en el albergue.
  - `404 Not Found`: Albergue no existe.
  - `403 Forbidden`: Usuario no asignado al albergue.

---

## 4. CATALOGO COMPLETO DE ENDPOINTS DEL SISTEMA

### 4.1 Modulo Publico (Ciudadano / Sin Autenticacion)

| Metodo | Endpoint | Parametros | Descripcion |
| :--- | :--- | :--- | :--- |
| `GET` | `/publico/ubicaciones` | Ninguno | Retorna GeoJSON/Array con todos los refugios activos y centros de acopio con sus coordenadas WGS84, capacidad, ocupacion y estado. |
| `GET` | `/publico/rutas/segura` | `origen_lat`, `origen_lon`, `destino_id`, `medio_transporte` | Traza una ruta de evacuacion optima evitando tramos viales anegados o inundados. |
| `GET` | `/publico/albergues/{id}` | `id` (UUID en path) | Retorna informacion publica detallada de un albergue en particular (sin revelar datos medicos ni nombres de personas). |
| `GET` | `/utils/health-check` | Ninguno | Chequeo de salud del servicio (retorna `true`). |

### 4.2 Modulo de Autenticacion y Usuarios

| Metodo | Endpoint | Formato | Descripcion |
| :--- | :--- | :--- | :--- |
| `POST` | `/login/access-token` | `application/x-www-form-urlencoded`<br>`username`, `password` | Autenticacion OAuth2 Password Bearer. Retorna token JWT y rol. |
| `POST` | `/login/test-token` | `Bearer <token>` | Valida la vigencia y decodifica el token actual. |
| `GET` | `/users/me` | `Bearer <token>` | Obtiene los datos del perfil del usuario conectado (id, email, rol, nombre). |
| `PATCH` | `/users/me` | `Bearer <token>` | Actualiza datos personales del usuario activo. |
| `PATCH` | `/users/me/password` | `Bearer <token>` | Cambio de clave del usuario activo. |
| `GET` | `/users/` | `Bearer <token>` (Superadmin) | Lista usuarios del sistema con paginacion (`skip`, `limit`). |
| `POST` | `/users/` | `Bearer <token>` (Superadmin) | Creacion de nuevos usuarios y asignacion de roles operativos. |

### 4.3 Modulo de Gestion Operativa de Albergues (`/albergues`)

| Metodo | Endpoint | Rol Requerido | Descripcion |
| :--- | :--- | :--- | :--- |
| `GET` | `/albergues/` | Autenticado | Lista todos los albergues con sus capacidades operativas. |
| `POST` | `/albergues/` | Coordinador / Superadmin | Crea un nuevo albergue en el sistema. |
| `POST` | `/albergues/carga-masiva` | Coordinador / Superadmin | Importa o actualiza por lotes albergues oficiales inicializando sus inventarios. |
| `GET` | `/albergues/{id}` | Personal Asignado | Obtiene detalle operativo completo del albergue. |
| `PUT` | `/albergues/{id}` | Admin Albergue / Coord. | Actualiza datos generales y estado operativo del albergue. |
| `GET` | `/albergues/{id}/infraestructura` | Personal Asignado | Consulta las 9 areas fisicas segun el contrato frontend. |
| `POST` | `/albergues/{id}/infraestructura/{areaId}/ajuste` | Admin Albergue | Ajuste atomico (+/-) de un area fisica especifica. |
| `POST` | `/albergues/{id}/ingreso-familiar` | Admin Albergue | Admision individual o de grupo familiar con validacion atomica de cupo. |
| `GET` | `/albergues/{id}/refugiados` | Personal Asignado | Listado de personas albergadas (anonimizando datos medicos a personal no medico). |
| `GET` | `/albergues/{id}/familias` | Personal Asignado | Listado de grupos familiares activos en el albergue. |
| `GET` | `/albergues/{id}/suministros` | Personal Asignado | Inventario actual de agua, alimentos, cobijas, botiquines, etc. |
| `PUT` | `/albergues/{id}/suministros` | Admin Albergue | Actualizacion de existencias de suministros criticos. |
| `GET` | `/albergues/{id}/personal` | Personal Asignado | Personal asignado y recursos humanos operativos por turno. |

---

## 5. CATALOGO DE ALBERGUES VERIDICOS SEMBRADOS EN EL SISTEMA

Los siguientes 14 inmuebles corresponden a registros verificados de los catalogos estatales de Proteccion Civil (Tamaulipas 2025 y Veracruz):

| Folio Oficial | Nombre del Inmueble | Municipio | Estado | Coordenadas (Lat, Lon) | Capacidad |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `VER-POZ-001` | Casa del Migrante | Poza Rica de Hidalgo | Veracruz | `20.507247, -97.461041` | 80 |
| `VER-POZ-002` | Centro Recreativo del SUTERM | Poza Rica de Hidalgo | Veracruz | `20.507290, -97.462200` | 120 |
| `VER-POZ-003` | Casa de la Cultura | Poza Rica de Hidalgo | Veracruz | `20.514920, -97.447150` | 100 |
| `VER-POZ-004` | Instalacion de Proteccion Civil Municipal | Poza Rica de Hidalgo | Veracruz | `20.514800, -97.447200` | 150 |
| `VER-ALA-001` | Escuela Primaria Enrique C. Rebsamen | Alamo Temapache | Veracruz | `20.901060, -97.682055` | 100 |
| `VER-PAN-001` | Secundaria para Trabajadores E. T. Trimmer | Panuco | Veracruz | `22.053564, -98.182059` | 120 |
| `TAM-ALD-001` | Escuela Primaria Pedro Jose Mendez | Aldama | Tamaulipas | `23.301230, -98.073984` | 50 |
| `TAM-NLD-001` | Refugio Temporal Casa del Indigente | Nuevo Laredo | Tamaulipas | `27.488043, -99.508937` | 150 |
| `TAM-SNC-001` | Clinica IMSS del Ejido Flechadores | San Nicolas | Tamaulipas | `24.522111, -98.678127` | 30 |
| `TAM-VHE-001` | Proteccion Civil y Bomberos | Valle Hermoso | Tamaulipas | `25.666273, -97.826541` | 80 |
| `TAM-VIC-001` | Centro de Convivencia No. 4 | Victoria | Tamaulipas | `23.750945, -99.150649` | 50 |
| `TAM-RBR-001` | Departamento de Proteccion Civil | Rio Bravo | Tamaulipas | `25.982206, -98.110500` | 320 |
| `TAM-TAM-001` | Escuela Primaria Nuevo Santander | Altamira | Tamaulipas | `22.363848, -97.904238` | 100 |
| `TAM-TAM-002` | Parroquia Santo Angel | Tampico | Tamaulipas | `22.260080, -97.865916` | 80 |

---

## 6. CREDENCIALES PRECONFIGURADAS DE PRUEBA Y DEMOSTRACION

| Rol Operativo | Correo Electronico | Clave de Acceso | Alcance y Permisos |
| :--- | :--- | :--- | :--- |
| **Superadmin / Coordinador PC** | `admin@proteccioncivil.gob.mx` | `Admin1234!` | Acceso irrestricto, carga masiva, todas las rutas de administracion. |
| **Admin Albergue (Polideportivo)** | `javier@proteccioncivil.gob.mx` | `Javier1234!` | Gestion de Infraestructura e Ingreso Familiar en Polideportivo Oriente. |

---

*Documento consolidado conforme a la Constitucion del Aldraverso y el protocolo de soberania tecnica.*
