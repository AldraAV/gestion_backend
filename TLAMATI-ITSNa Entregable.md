**![](data:image/png;base64...)![](data:image/png;base64...)Tecnológico Nacional de México**

![](data:image/png;base64...)

**HackaTec Etapa Regional**

**Región 02**

“SIGRAS”

**Temática:** Sistema Inteligente de Gestión de Rutas Seguras

**Categoría:** Tecnologías para la gestión pública

TLAMATI\_\_ITSNa

**Integrantes:**

|  |  |
| --- | --- |
| 241H0226- José Avilés Cárdenas | Ing. Tecnologías de la información y comunicaciones |
| 231H0135- Diego Alonso Benito de la Cruz | Ing. Tecnologías de la información y comunicaciones |
| 241H0087- Sury Jael Cristino Arteaga | Ing. Logística |
| 231H0139- Ana Iveth González Loaiza | Ing. Tecnologías de la información y comunicaciones |
| 231H0154- Javier Mar Cruz | Ing. Tecnologías de la información y comunicaciones |

**Asesor:**

Mtro. José Alberto Vicencio Lorenzo

**Indice**

[**Definición del problema** 3](#_Toc229733714)

[**Propuesta de solución** 4](#_Toc229733715)

[**Asignación de roles de trabajo** 6](#_Toc229733716)

[**Product Backlog** 7](#_Toc229733717)

[**Cronograma de actividades** 8](#_Toc229733718)

[**Herramientas tecnológicas empleadas para el desarrollo de la propuesta** 9](#_Toc229733719)

[**Especificacion técnica de la propuesta** 10](#_Toc229733720)

[**Ejes Transversales** 11](#_Toc229733721)

[**Referencias bibliográficas** 12](#_Toc229733722)

# **Definición del problema**

La zona norte de Veracruz cuenta con una riqueza de recursos hídricos, sin embargo, esa misma condición la vuelve vulnerable ante los fenómenos hidrometereológicos. De acuerdo con el INEGI (Instituto Nacional de Estadistica y Geografía, 2025) las lluvias intensas, los ciclones tropicales y las inundaciones generan las mayores afectaciones sociales y económicas en el estado. Dentro del Atlas Nacional de Riesgos elaborado por el Centro Nacional de Desastres (CENAPRED) ubicada a gran parte del norte veracruzano dentro de las zonas con mayor exposición a inundaciones.

En octubre de 2025 el desbordamiento de los ríos Cazones y Pantepec afectó a 55 municipios dañando más de 16 000 viviendas. En estas emergencias, la evacuación depende de avisos verbales y de la experiencia personal de protección civil debido a que no existe una herramienta que indique en tiempo real que calles son transitables, que refugio temporal más cercano con espacio disponible. Como solución a esta problemática se propone un sistema inteligente de gestión de rutas seguras para la población. Con ello se busca reducir el tiempo de evacuación, evitar que las familias transiten por calles inundadas y apoyar la toma de decisiones de los gobiernos del estado y municipales.

# **Propuesta de solución**

SIGRAS (Sistema inteligente de gestión de rutas seguras para la población), es un sistema responsivo que asigna rutas de evacuación seguras a la población durante emergencias por inundaciones, mediante un sistema de posicionamiento global GPS, inteligencia artificial, dirigida principalmente. Su innovación radica en la integración de geolocalización GPS, APIS que integran grafos viales. El sistema cuenta con un panel para Protección Civil que emite alertas por colonia, registra tramos inundados, coordinar brigadas en vivo y controla el aforo de refugios; así como una interfaz móvil ciudadana que guía al usuario hacia el albergue asignado. Si una calle se inunda o un refugio se satura, las rutas se recalculan dinámicamente en segundos.

A diferencia de otros sistemas, SIGRAS incluye un módulo participativo de reporte ciudadano de incidencias y utiliza herramientas de código abierto, garantizando una implementación económica y accesible que fortalece la toma de decisiones gubernamentales ante el desbordamiento de ríos; a nivel nacional, es un modelo de transferencia tecnológica altamente replicable; y a nivel internacional, contribuye directamente al ODS 11 (Ciudades y Comunidades Sostenibles) al elevar la resiliencia comunitaria y salvaguardar la vida de la población.

**Metodología**

El desarrollo de “SIGRAS” se realizó mediante la metodología SCRUM, permitiendo organizar las actividades del equipo de trabajo a través de iteraciones cortas y procesos colaborativos. Una de las primeras actividades fue la definición de roles del equipo de trabajo, estableciendo las responsabilidades como Product Owner, Scrum Master y como Development team todos los integrantes del equipo, para garantizar una correcta administración del proyecto.

Posteriormente, se generó el Product backlog, donde se identificaron y priorizaron las historias de usuario relacionadas con el cálculo de rutas seguras, la asignación de refugios, el monitoreo GPS y las alertas de evacuación. A partir de ello se llevaron a cabo reuniones sprint planning para definir actividades correspondientes a cada sprint de desarrollo. Durante el proceso, se realizaron reuniones Daily Scrum de seguimiento y control para supervisar avances, detectar problemas y coordinar tareas entre los integrantes. Finalmente, se ejecutaron pruebas funcionales y revisiones del sistema mediante Sprint Review, permitiendo evaluar resultados y realizar mejoras continuas al prototipo.

**Figura 1.**

Diseño del proceso de la metodología Scrum.

![](data:image/jpeg;base64...)

## **Product Backlog**

**Tabla 1.**

Product Backlog del Sistema “SIGRAS”.

|  |  |  |
| --- | --- | --- |
| No. | Historia de usuario | Prioridad |
| 1.- | Como administrador de protección civil quiero registrar refugios con ubicación y capacidad. | Alta |
| 2.- | Como ciudadano, quiero ver mi ubicación y la ruta más segura al refugio más cercano. | Alta |
| 3.- | Como administrador, quiero que el sistema asigne a cada sector el refugio con espacio disponible. | Alta |
| 4.- | Como brigadista, quiero compartir mi ubicación GPS en tiempo real. | Alta |
| 5.- | Como coordinador, quiero ver en el mapa la posición de todas las brigadas. | Alta |
| 6.- | Como administrador, quiero actualizar la ocupación de los refugios. | Alta |
| 7.- | Como ciudadanos, quiero consultar el sistema desde mi celular de forma sencilla. | Media |

## **Cronograma de actividades**

|  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **Actividad** | **Descripción** | **1-3 Hrs** | **4-8 Hrs** | **9-14 Hrs** | **15-26 Hrs** | **27-32 Hrs** | **33-36 Hrs** |
| **Sprint 0:** Planeación | Organización del equipo, asignación de roles y definición de requerimientos |  |  |  |  |  |  |
| **Sprint 1:** Análisis y definición | Diagnóstico de la problemática en zonas de riesgo del norte de Veracruz, catalogación de refugios y estructuración del Product backlog |  |  |  |  |  |  |
| **Sprint 2:** Diseño y arquitectura | Diseño de arquitectura, base de datos e interfaz web responsiva. |  |  |  |  |  |  |
| **Sprint 3:** Desarrollo de módulos | Programación del backend, estructuración, algoritmos e integración de la API GPS. |  |  |  |  |  |  |
| **Sprint 4:** Pruebas y validación | Validación de geolocalización GPS, pruebas de asignación y alertas vis WebSockets. |  |  |  |  |  |  |
| **Sprint 5:** Ajustes finales y presentación de proyecto | Correcciones, documentación y preparación de exposición. |  |  |  |  |  |  |

# **Herramientas tecnológicas empleadas**

Para el desarrollo de SIGRAS se emplean herramientas de software orientadas en infraestructura tecnológica de desarrollo web y geolocalización. En el backend, se utiliza el lenguaje Python con el marco de trabajo FastAPI especializada en el desarrollo de para la lógica alojado en cloud hosting Render. Para la gestión de datos, se implemento supabase como base de datos centralizada en la nube. Para el Fronted, se integro la API de MapBox para la visualización interactiva y el trazo de rutas optimizadas mediante variaciones del algoritmo Dijkstra, desplegando la plataforma digital en Vercel. La maquetación de interfaces se realizo en Figma, la codificación en Visual studio Code y GPS integrado para la transmisión y captura de coordenadas en tiempo real. Estas tecnologías permiten construir una plataforma accesible y eficiente para la ciudadanía ante desastres naturales.

La programación se llevo a cabo a través de la metodología de trabajo SCRUM mediante herramientas colaborativas de planificación y seguimiento de las actividades correspondientes.

# **Especificación técnica de la propuesta**

Para el desarrollo de SIGRAS se emplean herramientas de software orientadas a la protección civil, gestión de riesgos hidrometereológicos. En el backend se implementa Python junto con el framework FastAPI, garantizando una alta eficiencia en el procesamiento de datos, en dicha capa destaca la implementación de un modelo de IA la cual analiza los reportes de siniestros emitidos por los ciudadanos. La misma se encargará de procesarlos, asignarlos automáticamente en el mapa delimitando zonas de riesgo de forma precisa; la lógica esta soportada por una data base alojada en Supabase, el backend alojado en Render, así como las APIS geoespaciales asegurando el trazado de rutas de evacuación seguras.

Para el fronted, desplegado en Vercel, se usa React JS para construir una interfaz web dinámica y responsiva, facilitando la navegación del usuario y el monitoreo gubernamental, desarrollado en Visual Studio Code con control de versiones en GitHub, mientras que para la maquetación y documentación se usa canva y herramientas de ofimática.

La organización del proyecto se llevó a través de la metodología de trabajo SCRUM mediante herramientas colaborativas de planificación y seguimiento de las actividades correspondientes.

**Figura 2.**

Modelo entidad relación.

**Figura 3.**

Diagrama de proceso del sistema.

![](data:image/png;base64...)

**Figura 4.**

Arquitectura del sistema.

![](data:image/png;base64...)

# **Ejes Transversales**

SIGRAS tendrá un impacto en la protección civil mediante un sistema web enfocado a la gestión inteligente de riesgos hidrometereológicos, en el eje de inclusión y equidad, el sistema democratiza el acceso a la seguridad al facilitar rutas de evacuación claras para cualquier ciudadano con un dispositivo móvil, priorizando a comunidades ubicadas en zonas vulnerables.

En cuanto al impacto social, la propuesta salvaguarda vidas al mitigar el caos durante contingencias, agilizando la respuesta gubernamental y fortaleciendo la resiliencia comunitaria mediante el mapeo colaborativo, así mejorar la logística operativa del personal de Protección Civil. Respecto a la sustentabilidad, SIGRAS promueve la creación de ciudades resilientes mediante la digitalización de inventarios en refugios y la optimización de recursos, reduciendo los tiempos de traslado y el consumo de combustible en los vehículos de rescate.

Finalmente, en tecnologías emergentes, el sistema integra herramientas modernas de enrutamiento dinámico, análisis geoespacial y procesamiento de reportes ciudadanos mediante Inteligencia Artificial, consolidando la transformación digital en la prevención y gestión de desastres.

# **Modelo de negocio (Business Model Canvas)**

El proyecto conecta ciudadanía en riesgo, centros de acopio y autoridades mediante una plataforma B2G dividida dos secciones: consulta de rutas seguras para la población y gestión de personal e inventario. En la propuesta de valor resuelve la segmentación de información, cuellos de botella en líneas de emergencias. Se caracteriza por ser de uso bidireccional, con posibilidad de estabilidad y basada en datos verídicos.

El canal de difusión es un sistema web donde los ciudadanos visualizan mapas, rutas y generan reportes, mientras los administradores gestionan y actualizan la información de albergues, insumos e infraestructuras.

Los recursos clave incluyen infraestructura en la nube, APIs de mapas/clima, algoritmos de ruteo y predicción, y equipo técnico especializado. Las actividades clave son monitoreo y verificación de reportes, actualización de rutas y coordinación de datos. Los socios estratégicos son Protección Civil, Cruz Roja, Sistema Metrológico Nacional, gobiernos municipales y SINAPROC. Los ingresos provienen de contratos institucionales (GovTech), sin costo para el ciudadano. Los costos cubren desarrollo, infraestructura, personal, adopción y normativas.

*![](data:image/png;base64...)Visualización del modelo canva de 9 capas SIGRAS.*

# **Validación del modelo de negocio**

Mediante la metodología Customer Development, el equipo validó consultas, encuestas y entrevistas a 84 usuarios, socios clave y potenciales. Los resultados muestran una aceptación contundente: el 77.4% considera altamente necesaria la herramienta (calificación de 4 o 5) y el 67.9% prefiere consultar aplicaciones o sitios web oficiales durante una emergencia.

Frente a las contingencias, el 42.9% señala como principal obstáculo la falta de datos sobre rutas de evacuación o vías colapsadas, y el 33.3% desconoce la ubicación o capacidad de albergues. En conjunto, representan el 76.2% de las necesidades informativas que SIGRAS resolverá mediante un mapa en tiempo real.

Para reportar zonas de riesgo, el 52.4% prioriza enviar fotografías con geolocalización rápida, superando a las llamadas de emergencia (27.4%) y las redes sociales (20.2%). En el ámbito operativo, el 65.5% considera indispensable integrar la gestión de insumos y capacidad en una sola pantalla, un 16.7% valora el registro digital de entradas y salidas, mientras que un 15.5% solicita indicadores de capacidad. Estos datos confirman la viabilidad del proyecto antes de intervenir recursos y validan la digitalización en refugios y centros de acopio.

![](data:image/png;base64...)**Resultados de la validación encuesta en relación a las necesidades del sistema.**

# **Resultados preliminares de la encuestas.**

![](data:image/png;base64...)

# **Proyección de costos**

La propuesta estima los recursos financieros necesarios para llevar el sistema desde su validación piloto hasta su comercialización con gobiernos estatales, mediante un modelo de suscripción anual. La inversión inicial de $77,364.00 cubre registro de marca, dominio, certificado SSL, diseño de marca, equipo de cómputo, equipo de oficina, capital de trabajo y equipos auxiliares, proyectando depreciación anual de $8,046.00 a 5 años.

Los costos de escalamiento se dividen en variables como hosting, APIs de mapas e inteligencia artificial, licencias de software y fijos sueldos del equipo de desarrollo, gastos de oficina, internet, resultando en un costo unitario total de $2,563.14 por licencia anual.

Se busca un margen de ganancia del 30%, fijando el precio de venta en $3,460.24 por licencia, con incremento anual del 5% conforme se amplía la cobertura y se incorporan nuevas funcionalidades. Los costos de soporte técnico, capacitación a centros de acopio y autoridades, y mantenimiento continuo están incluidos dentro del costo fijo mensual.

Estimando un punto de equilibrio con 11.76 unidades mensuales con proyección de ventas de 14 licencias desde el primer año. El modelo nos permite recuperar la inversión inicial en menos de dos años, verifica la viabilidad económica con escalamiento estatal en Veracruz.

*![](data:image/png;base64...)Planteamiento de inversión inicial.*

*Análisis del punto de equilibrio.*

![](data:image/png;base64...)

# **Referencias bibliográficas**

Ávila Pérez, É. (11 de 10 de 2025). *EL UNIVERSAL*. Obtenido de https://www.eluniversal.com.mx/estados/suman-5-muertos-55-municipios-afectados-y-16-mil-casas-danadas-en-veracruz/

Instituto Nacional de Estadistica y Geografía. (2025). *Reducción del riesgo por avenidas, desbordamientos de ríos e inundaciones.* Obtenido de https://www.veracruz.gob.mx/proteccioncivil/wp-content/uploads/sites/5/2025/05/Recpobavenidas\_desbordamientos-2025.pdf

México, G. d. (s.f.). *https://www.cenapred.gob.mx/es/Publicaciones/archivos/297-INFOGRAFAATLASDERIESGOS.PDF*.

Protección civil. (2024). *Atlas de Riesgos del Estado de Veracruz.* Obtenido de https://www.veracruz.gob.mx/proteccioncivil/wp-content/uploads/sites/5/2024/10/Atlas-de-Riesgos-del-Estado-de-Veracruz\_.pdf

Welcome to the united nations. (s.f.). *Ciudades- Desarrollo Sustentable*. Obtenido de https://www.un.org/sustainabledevelopment/es/cities/