# BRIEF FUNDACIONAL: SIGRAS
## Sistema Inteligente de Gestión de Rutas y Alertas Seguras

**Proyecto:** HackaTec 2026 - Protección Civil  
**Modelo Comercial:** SaaS B2G (Business-to-Government)  

---

### 1. OBJETIVO PRINCIPAL
Desarrollar un sistema de alertas avanzado y geoespacial para la ciudadanía en situación de vulnerabilidad durante desastres naturales. El sistema busca agilizar la localización de centros de ayuda y rutas de movilidad seguras, auxiliar a los centros de acopio y albergues en el control de sus suministros y capacidad de alojamiento, e identificar zonas de riesgo a través de reportes ciudadanos en tiempo real.

---

### 2. JERARQUÍAS DE USUARIOS

El ecosistema de SIGRAS se divide estructuralmente en dos grandes capas de interacción:

#### A. Nivel Administrativo (Organizaciones Públicas de Protección Civil)
Son los operadores del sistema y los clientes principales del modelo B2G. Tienen acceso integral al *dashboard* de control.
- **Responsabilidades:** Gestión y actualización de inventarios de suministros, habilitación y monitoreo de la capacidad de los albergues, validación de reportes ciudadanos y emisión de alertas críticas para la población.

#### B. Nivel Civil (Usuario Final / Ciudadanía)
Es el usuario "sensible". Este usuario requiere interfaces limpias, accesibles y directas para salvar su vida e integridad.
- **Responsabilidades:** Recepción de alertas tempranas, consulta de rutas de evacuación y disponibilidad de albergues cercanos. Emisión de reportes de emergencia y riesgos (inundaciones, derrumbes, etc.) desde la zona cero.

---

### 3. INNOVACIÓN TECNOLÓGICA: IA GEOESPACIAL Y MAPBOX

El núcleo innovador de SIGRAS reside en la integración de modelos de Inteligencia Artificial (LLMs) trabajando en conjunto con el motor de mapas **MapBox** a través de la arquitectura de **Tool Calling** (Llamada a Herramientas).

La IA funcionará como un asistente en la "Sala de Crisis" virtual:
1. **Construcción Dinámica del Mapa:** Los modelos de IA analizarán los datos entrantes del lado administrativo y los reportes ciudadanos en tiempo real, invocando herramientas (`tools`) específicas para manipular la interfaz del mapa.
2. **Generación de Polígonos de Riesgo:** La IA utilizará *Tool Calling* para dibujar áreas de peligro en el mapa basándose en la densidad de reportes ciudadanos o datos de sensores.
3. **Trazado de Rutas Seguras:** Ante un bloqueo reportado, la IA calculará y renderizará en el mapa de MapBox la ruta alternativa más segura para dirigir a los civiles al albergue con mayor capacidad.
4. **Agentes Autónomos de Triaje:** El modelo evaluará el nivel de urgencia de los mensajes o reportes ciudadanos y categorizará visualmente los incidentes en el mapa.

### 4. ECOSISTEMA DE MODELOS (VERIFICACIÓN DE TOOL CALLING)
Se ha verificado la infraestructura de APIs disponible en el entorno. Los siguientes proveedores garantizan un soporte robusto para **Tool Calling**, permitiendo la interacción directa con el mapa:
- **Groq (Llama 3 / Mixtral):** Alta velocidad para inferencia reactiva en tiempo real y excelente soporte para *Tool Calling*.
- **Gemini (Flash / Pro):** Soporte nativo y altamente estructurado para el uso de herramientas.
- **Mistral:** Capacidades nativas de *Function Calling* sólidas.
- **Cohere (Command R / R+):** Modelos específicamente entrenados para orquestación de herramientas complejas.
- **Cerebras / OpenRouter:** Soporte dependiendo del modelo subyacente (ej. Meta Llama 3.1).
