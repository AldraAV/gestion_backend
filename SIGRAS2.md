Pero no quiero solamente a Veracruz, sino utilizar datos de ejemplo. Estadísticos por ejemplo al principio pero lo demás en el resto. O sea, México

Entiendo: quieres que **todo el proyecto de SIGRAS tenga alcance nacional**, utilizando Veracruz únicamente como antecedente o escenario de demostración, no como el mercado ni como el único caso de uso.

## Enfoque correcto

La estructura debe ser:

```text
México: problemática y estadísticas nacionales
        ↓
Escenario de demostración: datos simulados
        ↓
SIGRAS: solución adaptable a cualquier estado o municipio
        ↓
Mercado: gobiernos municipales, estatales y federal
```

La inundación del norte de Veracruz sirve para contextualizar la urgencia, pero el producto debe poder operar con datos de ejemplo de cualquier entidad federativa.

## Problemática nacional

México enfrenta pérdidas humanas, patrimoniales, económicas y de infraestructura por fenómenos naturales y antropogénicos.

De acuerdo con el Programa Nacional de Protección Civil 2026–2030, durante 2024 se registraron 283 desastres, 633 defunciones y daños y pérdidas estimados en 14,434 millones de pesos. Los fenómenos hidrometeorológicos representaron 83.6% de las pérdidas registradas.[1][2]

El mismo programa señala que alrededor de 60 millones de personas sufrieron afectaciones directas o indirectas durante el periodo analizado, ya fuera por pérdida de patrimonio o de medios de vida.[1]

México cuenta con el Atlas Nacional de Riesgos, que integra información cartográfica sobre peligro, exposición, vulnerabilidad y riesgo.  Sin embargo, durante una emergencia la información operativa puede permanecer fragmentada entre ciudadanía, municipios, estados, refugios, centros de acopio, cuerpos de auxilio y dependencias.[3]

El problema nacional es:

> La falta de una capa operativa común que permita transformar reportes, riesgos, capacidades y necesidades en decisiones coordinadas durante una emergencia.

## Caso de referencia

La inundación de la zona norte de Veracruz, con afectaciones en municipios como Poza Rica, Álamo y Pánuco, puede utilizarse para mostrar la urgencia del problema.

No debe presentarse como el único contexto del sistema. Debe mencionarse como:

> Un caso reciente que evidencia las dificultades de coordinación, comunicación, movilidad, alojamiento y distribución de suministros durante una emergencia.

Las cifras de personas fallecidas, viviendas afectadas y daños materiales deben manejarse con fecha y fuente, porque variaron conforme avanzaron los censos. No deben convertirse en el único fundamento estadístico del proyecto.

## Alcance nacional de SIGRAS

### Definición

> SIGRAS es una plataforma digital nacional de apoyo a la gestión integral de riesgos que integra reportes ciudadanos, zonas de peligro, refugios, centros de acopio, rutas y capacidades de respuesta para mejorar la coordinación de autoridades y población durante emergencias.

### Cobertura

SIGRAS puede utilizarse en:

- Municipios.
- Entidades federativas.
- Coordinaciones regionales.
- Dependencias federales.
- Sistemas estatales de Protección Civil.
- Unidades municipales de Protección Civil.

### Fenómenos

La plataforma puede adaptarse a:

- Inundaciones.
- Huracanes.
- Lluvias intensas.
- Deslaves.
- Sismos.
- Incendios forestales.
- Sequías.
- Olas de calor.
- Accidentes químicos.
- Evacuaciones.
- Emergencias sanitarias.
- Fallas en infraestructura crítica.

## Uso de datos de ejemplo

Para el prototipo no necesitan contar con información operativa real de todos los estados.

Pueden construir un escenario nacional simulado con:

- Estados.
- Municipios.
- Población.
- Zonas de riesgo.
- Reportes ciudadanos.
- Refugios.
- Centros de acopio.
- Inventario.
- Rutas.
- Hospitales.
- Personas vulnerables.
- Estado de atención.

Los datos deben marcarse como:

> **Datos de ejemplo para demostración del prototipo.**

No deben presentarse como información oficial en tiempo real.

## Escenario de demostración

El escenario puede utilizar tres entidades con perfiles de riesgo distintos, por ejemplo:

- Veracruz: inundación.
- Guerrero: huracán.
- Oaxaca: deslave.

Así se demuestra que SIGRAS no depende de un único desastre ni de una sola entidad.

### Ejemplo de datos simulados

| Entidad | Municipio | Evento | Reportes | Refugios | Prioridad |
|---|---|---|---:|---:|---|
| Veracruz | Poza Rica | Inundación | 126 | 8 | Alta |
| Guerrero | Acapulco | Huracán | 94 | 12 | Alta |
| Oaxaca | Santa María | Deslave | 41 | 4 | Crítica |

Estos datos son únicamente ilustrativos y deben ser sustituidos por información validada si el proyecto pasa a una etapa piloto.

## Funcionamiento nacional

```text
1. Se registra una emergencia.
2. Se selecciona la entidad y municipio.
3. La ciudadanía envía reportes.
4. El sistema georreferencia y clasifica los reportes.
5. Se identifican personas vulnerables.
6. Se revisan refugios disponibles.
7. Se consulta el inventario de centros de acopio.
8. Se identifican rutas bloqueadas.
9. Se priorizan zonas y solicitudes.
10. Se asignan recursos o responsables.
11. Se actualiza el estado de atención.
12. Se generan indicadores para las autoridades.
```

## Módulos de la plataforma

### Reportes ciudadanos

- Registro de ubicación.
- Tipo de afectación.
- Personas afectadas.
- Necesidades.
- Evidencia.
- Nivel de urgencia.
- Estado del reporte.

### Refugios

- Ubicación.
- Capacidad total.
- Ocupación.
- Espacios disponibles.
- Servicios.
- Accesibilidad.
- Estado operativo.

### Centros de acopio

- Inventario.
- Entradas.
- Salidas.
- Necesidades.
- Capacidad.
- Responsable.
- Entregas.

### Rutas y movilidad

- Caminos bloqueados.
- Rutas seguras.
- Puentes afectados.
- Hospitales.
- Refugios.
- Centros de ayuda.
- Tiempos estimados.

### Mapa de riesgos

- Zonas de peligro.
- Exposición.
- Vulnerabilidad.
- Reportes ciudadanos.
- Infraestructura crítica.
- Nivel de prioridad.

### Panel de coordinación

- Emergencias activas.
- Reportes pendientes.
- Zonas críticas.
- Refugios disponibles.
- Inventarios.
- Recursos asignados.
- Municipios afectados.
- Tiempos de atención.

## Modelo de negocio nacional

SIGRAS se vendería bajo un modelo **Business to Government**.

### Clientes potenciales

- Gobiernos municipales.
- Gobiernos estatales.
- Coordinación Nacional de Protección Civil.
- Dependencias federales.
- Sistemas estatales de Protección Civil.
- Unidades municipales.
- Organismos de atención y respuesta.

### Oferta comercial

- Implementación inicial.
- Configuración por entidad.
- Licencia institucional.
- Soporte y mantenimiento.
- Capacitación.
- Integración de datos.
- Módulos especializados.
- Operación administrada.
- Escalamiento multientidad.

### Fases de adopción

| Fase | Alcance |
|---|---|
| Prototipo | Datos de ejemplo y simulación |
| Piloto | Un municipio o grupo de municipios |
| Estatal | Integración de varios municipios |
| Regional | Coordinación de entidades |
| Nacional | Interoperabilidad con sistemas federales |

## Cómo presentarlo en HackaTec

No deben decir:

> “SIGRAS es una aplicación para Veracruz.”

Deben decir:

> “SIGRAS es una plataforma nacional adaptable a distintos riesgos y territorios. Para demostrar su funcionamiento utilizamos un escenario simulado basado en una inundación de la zona norte de Veracruz.”

La presentación debe incluir:

1. Estadísticas nacionales.
2. Problema de coordinación.
3. Caso de referencia.
4. Datos de ejemplo.
5. Flujo funcional.
6. Panel de autoridades.
7. Reporte ciudadano.
8. Refugios y acopios.
9. Priorización.
10. Escalabilidad nacional.

## Redacción recomendada

> México enfrenta desastres naturales y antropogénicos que provocan pérdidas humanas, afectaciones patrimoniales y presión sobre las capacidades institucionales de respuesta. Aunque existen instrumentos como el Atlas Nacional de Riesgos, sistemas de Protección Civil y protocolos de emergencia, la información operativa puede permanecer fragmentada entre ciudadanía, municipios, entidades federativas, refugios, centros de acopio y cuerpos de auxilio. SIGRAS propone una plataforma nacional de apoyo a la gestión integral de riesgos que centraliza reportes, capacidades, rutas, refugios y necesidades para mejorar la priorización y coordinación durante emergencias. El caso de las inundaciones registradas en la zona norte de Veracruz se utiliza como escenario de referencia para demostrar el funcionamiento del prototipo, pero la solución está diseñada para adaptarse a cualquier entidad, municipio o fenómeno perturbador del país.

## Definición final

> **SIGRAS es una plataforma nacional de gestión inteligente de riesgos que convierte reportes ciudadanos, mapas de peligro, capacidades de refugio, inventarios y rutas en decisiones coordinadas para proteger vidas y recursos durante emergencias en México.**

La idea queda así:

- **México** es el contexto.
- **Las estadísticas nacionales** justifican el problema.
- **Veracruz** es un caso de referencia.
- **Los datos de ejemplo** sirven para demostrar el prototipo.
- **SIGRAS** tiene alcance para cualquier estado, municipio o fenómeno.
- **El mercado** está formado por gobiernos municipales, estatales y federal.

Citas:
[1] PROGRAMA Nacional de Protección Civil 2026-2030. https://sidofqa.segob.gob.mx/notas/docFuente/5787683
[2] Resumen ejecutivo Impacto 2024 - cenapred.gob.mx https://www.cenapred.gob.mx/es/Publicaciones/archivos/521-RESUMENEJECUTIVOIMPACTO2024.PDF
[3] Atlas Nacional de Riesgos http://www.atlasnacionalderiesgos.gob.mx/
