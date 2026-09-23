# CATALOGO OPERATIVO DE REPOSITORIOS (MUACK / HERRAMIENTAS_GESTION)
# Formato estructurado en YAML para ingesta determinista de agentes autonomos
# Autor: Jose "Aldra" Aviles Cardenas
# Ecosistema: Aldraverso / HackaTec 2026

---
version: "2.0.0"
fecha_actualizacion: "2026-09-20"
ruta_base_repositorios: "C:/Users/carde/Desktop/MUACK/herramientas_gestion"

directiva_general_para_agentes:
  regla_1: "No intentes instalar repositorios clasificados como canibalizacion_logica. Romperas el entorno virtual."
  regla_2: "Para servicios plug_and_play, levantalos en un subproceso o terminal independiente y comunicate por HTTP."
  regla_3: "Toda funcion o logica extraida debe ser adaptada y tipada en espanol soberano."
  regla_4: "Prioriza siempre markitdown como dependencia instalable directa para conversion documental."

clasificacion_taxonomica:
  - categoria: "dependencias_instalables"
    descripcion: "Paquetes empaquetados que se instalan directamente con pip o uv en modo editable."
  - categoria: "servicios_plug_and_play"
    descripcion: "Servidores o proxies independientes que se ejecutan en un puerto y se consumen via HTTP."
  - categoria: "herramientas_cli"
    descripcion: "Utilidades ejecutables desde terminal para procesamiento y automatizacion previa."
  - categoria: "canibalizacion_logica"
    descripcion: "Monolitos o suites de donde unicamente se extraen funciones, algoritmos, regex o prompts especificos."
  - categoria: "referencia_recursos"
    descripcion: "Directorios documentales para consulta de infraestructura y tiers gratuitos."

repositorios:

  # ============================================================================
  # 1. DEPENDENCIAS INSTALABLES DIRECTAS
  # ============================================================================

  - id: "markitdown"
    nombre: "Microsoft MarkItDown"
    ruta_local: "C:/Users/carde/Desktop/MUACK/herramientas_gestion/markitdown"
    categoria_operativa: "dependencias_instalables"
    lenguaje_principal: "Python"
    descripcion_tecnica: "Motor universal de conversion documental a Markdown estructurado con preservacion de tablas."
    mecanismo_instalacion:
      comando_uv: 'uv add --editable "C:/Users/carde/Desktop/MUACK/herramientas_gestion/markitdown/packages/markitdown"'
      comando_pip: 'pip install -e "C:/Users/carde/Desktop/MUACK/herramientas_gestion/markitdown/packages/markitdown"'
    archivos_clave:
      - "packages/markitdown/src/markitdown/_markitdown.py"
    casos_de_uso:
      - "Conversion de contratos Word (.docx) a texto Markdown estructurado para LLMs."
      - "Conversion de presupuestos y catalogos de conceptos Excel (.xlsx) a tablas Markdown."
      - "Extraccion de texto limpio desde PDFs tecnicos y memorias de calculo."
    accion_agente: "Instalar en el entorno virtual de FastAPI e importar 'from markitdown import MarkItDown'. Usar 'convert_stream' o 'convert_file'."

  # ============================================================================
  # 2. SERVICIOS PLUG AND PLAY (SERVIDORES / PROXIES INDEPENDIENTES)
  # ============================================================================

  - id: "omniroute"
    nombre: "OmniRoute LLM Gateway"
    ruta_local: "C:/Users/carde/Desktop/MUACK/herramientas_gestion/OmniRoute"
    categoria_operativa: "servicios_plug_and_play"
    lenguaje_principal: "TypeScript / Node.js / Bun"
    descripcion_tecnica: "Gateway local compatible con OpenAI API que gestiona enrutamiento, conmutacion por error (failover) y balanceo entre multiples proveedores LLM."
    mecanismo_arranque:
      directorio: "C:/Users/carde/Desktop/MUACK/herramientas_gestion/OmniRoute"
      comando: "docker compose up -d"
      comando_alternativo: "pnpm dev"
      puerto_default: 8080
    endpoint_consumo: "http://localhost:8080/v1/chat/completions"
    casos_de_uso:
      - "Rotar automaticamente entre Groq, Google Gemini y OpenRouter cuando uno agote su cuota gratuita (Error 429)."
      - "Centralizar la telemetria de latencia y costos de inferencia en un solo punto."
    accion_agente: "No importar codigo. Si se requiere failover externo, levantar el servicio y apuntar el cliente httpx de FastAPI al puerto local de OmniRoute."

  - id: "freellmapi"
    nombre: "Free LLM API Gateway"
    ruta_local: "C:/Users/carde/Desktop/MUACK/herramientas_gestion/freellmapi"
    categoria_operativa: "servicios_plug_and_play"
    lenguaje_principal: "Node.js"
    descripcion_tecnica: "Proxy inverso que unifica accesos a capas gratuitas de modelos y expone una API compatible con OpenAI."
    mecanismo_arranque:
      directorio: "C:/Users/carde/Desktop/MUACK/herramientas_gestion/freellmapi"
      comando: "npm install && npm start"
      puerto_default: 3000
    endpoint_consumo: "http://localhost:3000/v1/chat/completions"
    casos_de_uso:
      - "Consumir modelos gratuitos sin exponer llaves directas en desarrollo temprano."
    accion_agente: "Levantar en terminal secundaria si se requiere respaldo de tokens gratuitos adicionales."

  - id: "freetoken"
    nombre: "FreeToken Edge Server"
    ruta_local: "C:/Users/carde/Desktop/MUACK/herramientas_gestion/FreeToken"
    categoria_operativa: "servicios_plug_and_play"
    lenguaje_principal: "Rust / C++ / Go"
    descripcion_tecnica: "Servidor de borde para gestion optimizada de tokens y modelos de pesos abiertos con algoritmos de atencion paginada."
    mecanismo_arranque:
      directorio: "C:/Users/carde/Desktop/MUACK/herramientas_gestion/FreeToken"
      comando: "cargo run --release"
    casos_de_uso:
      - "Servir inferencia ultrarrapida local en dispositivos de baja capacidad o borde."
    accion_agente: "Usar solo si se despliega inferencia local sin internet; de lo contrario, preferir APIs en la nube."

  - id: "anything-llm"
    nombre: "AnythingLLM Knowledge Suite"
    ruta_local: "C:/Users/carde/Desktop/MUACK/herramientas_gestion/anything-llm"
    categoria_operativa: "servicios_plug_and_play"
    lenguaje_principal: "Node.js / React / LanceDB"
    descripcion_tecnica: "Plataforma completa de gestion documental, vectorizacion automatica y chat RAG con aislamiento por espacios de trabajo."
    mecanismo_arranque:
      directorio: "C:/Users/carde/Desktop/MUACK/herramientas_gestion/anything-llm"
      comando: "docker-compose up -d"
      puerto_default: 3001
    casos_de_uso:
      - "Tener un sistema RAG corporativo listo para demostraciones sin programar la base vectorial."
    accion_agente: "Consumir exclusivamente a traves de su API REST (/api/v1/document/upload y /api/v1/workspace/chat)."

  # ============================================================================
  # 3. HERRAMIENTAS CLI Y UTILIDADES EJECUTABLES
  # ============================================================================

  - id: "context-mode"
    nombre: "Context-Mode Token Optimizer"
    ruta_local: "C:/Users/carde/Desktop/MUACK/herramientas_gestion/context-mode"
    categoria_operativa: "herramientas_cli"
    lenguaje_principal: "Node.js / Bun"
    descripcion_tecnica: "Herramienta de reduccion de hasta 98% de tokens mediante generacion de arboles sinopticos jerarquicos de archivos."
    archivos_clave:
      - "cli.bundle.mjs"
      - "server.bundle.mjs"
    mecanismo_ejecucion:
      comando: "node C:/Users/carde/Desktop/MUACK/herramientas_gestion/context-mode/cli.bundle.mjs --help"
    casos_de_uso:
      - "Comprimir carpetas masivas con 300 archivos XML o contratos de 150 paginas antes de enviarlos a contexto."
    accion_agente: "Invocar como subproceso CLI o extraer su algoritmo de digestion de sintaxis para integrarlo en Python."

  - id: "free-claude-code"
    nombre: "Free Claude Code CLI Harness"
    ruta_local: "C:/Users/carde/Desktop/MUACK/herramientas_gestion/free-claude-code"
    categoria_operativa: "herramientas_cli"
    lenguaje_principal: "Python / TypeScript"
    descripcion_tecnica: "Harness CLI que emula el ciclo operativo de programacion autonoma tipo Claude Code utilizando modelos alternativos."
    casos_de_uso:
      - "Automatizacion de edicion de codigo por lotes en consola durante el desarrollo."
    accion_agente: "Ejecutar en terminal como asistente de codigo independiente."

  - id: "camofox-browser"
    nombre: "Camofox Stealth Headless Browser"
    ruta_local: "C:/Users/carde/Desktop/MUACK/herramientas_gestion/camofox-browser"
    categoria_operativa: "herramientas_cli"
    lenguaje_principal: "C++ / Python / Playwright"
    descripcion_tecnica: "Navegador headless especializado en evasion de sistemas anti-bot (Cloudflare, Akamai) mediante falsificacion de huellas de hardware."
    casos_de_uso:
      - "Scraping y extraccion de datos en portales gubernamentales que bloquean solicitudes automatizadas comunes."
    accion_agente: "Llamar mediante subproceso o script de Playwright cuando un endpoint del SAT o portal publico devuelva bloqueo de bot."

  # ============================================================================
  # 4. REPOSITORIOS PARA CANIBALIZACION DE LOGICA (COPIAR Y ADAPTAR)
  # ============================================================================

  - id: "paperless-ngx"
    nombre: "Paperless-ngx"
    ruta_local: "C:/Users/carde/Desktop/MUACK/herramientas_gestion/paperless-ngx"
    categoria_operativa: "canibalizacion_logica"
    lenguaje_principal: "Python (Django)"
    descripcion_tecnica: "Suite de gestion documental y archivo historico con OCR, clasificacion automatica y hashing."
    modulos_a_canibalizar:
      - ruta: "src/documents/parsers.py"
        utilidad: "Algoritmos de sanitizacion de nombres de archivo y deteccion de tipos MIME seguros."
      - ruta: "src/documents/classifier.py"
        utilidad: "Logica de clasificacion heuristica de documentos mediante palabras clave."
      - ruta: "src/documents/matching.py"
        utilidad: "Expresiones regulares probadas para cazar fechas, montos y folios fiscales en textos escaneados."
    accion_agente: "NO INSTALAR. Abrir los archivos indicados, copiar las funciones especificas y colocarlas en nucleo/adaptadores/ con nomenclatura en espanol."

  - id: "dify"
    nombre: "Dify API & Workflow Engine"
    ruta_local: "C:/Users/carde/Desktop/MUACK/herramientas_gestion/dify"
    categoria_operativa: "canibalizacion_logica"
    lenguaje_principal: "Python (Flask) / Next.js"
    descripcion_tecnica: "Monolito de orquestacion de flujos LLM complejos, agentes y RAG hibrido."
    modulos_a_canibalizar:
      - utilidad_1: "Libreria 'json-repair' para reconstruir JSONs malformados emitidos por LLMs."
      - utilidad_2: "Estructura de prompts para dictamenes analiticos y extraccion de variables."
      - utilidad_3: "Logica de busqueda hibrida (fusion ponderada de distancias vectoriales y BM25)."
    accion_agente: "NO INSTALAR. Extraer patrones de prompts y la utilidad json-repair para robustecer el backend de FastAPI."

  - id: "mayan-edms"
    nombre: "Mayan EDMS"
    ruta_local: "C:/Users/carde/Desktop/MUACK/herramientas_gestion/Mayan-EDMS"
    categoria_operativa: "canibalizacion_logica"
    lenguaje_principal: "Python (Django)"
    descripcion_tecnica: "EDMS corporativo con cumplimiento legal, maquinas de estado y firmas digitales GPG."
    modulos_a_canibalizar:
      - concepto: "Maquina de estados finita para la transicion de expedientes de obra publica (Borrador -> Observado -> Solvente -> Aprobado)."
      - concepto: "Sellado de tiempo e inmutabilidad de metadatos."
    accion_agente: "Copiar la estructura logica del modelo de estados para gobernar las auditorias en SIGEDI."

  - id: "openkm-dms"
    nombre: "OpenKM Community"
    ruta_local: "C:/Users/carde/Desktop/MUACK/herramientas_gestion/openkm-dms"
    categoria_operativa: "canibalizacion_logica"
    lenguaje_principal: "Java"
    descripcion_tecnica: "Sistema de repositorio documental estructurado bajo el estandar JCR/CMIS."
    modulos_a_canibalizar:
      - concepto: "Diseno del arbol jerarquico de permisos institucionales (Contraloria, Tesoreria, Obras Publicas)."
    accion_agente: "Utilizar solo como referencia conceptual para el diseno de tablas y esquemas en base de datos."

  - id: "agentic-inbox"
    nombre: "Cloudflare Agentic Inbox"
    ruta_local: "C:/Users/carde/Desktop/MUACK/herramientas_gestion/agentic-inbox"
    categoria_operativa: "canibalizacion_logica"
    lenguaje_principal: "TypeScript / Cloudflare Workers"
    descripcion_tecnica: "Bandeja de correo entrante serverless que dispara agentes para procesar archivos adjuntos."
    modulos_a_canibalizar:
      - utilidad: "Flujo de desencadenamiento de tareas asincronas al recibir un archivo ZIP por correo."
    accion_agente: "Adaptar el patron a Python usando imap-tools o un webhook de recepcion de correo."

  - id: "orca"
    nombre: "Orca Parallel Agent Engine"
    ruta_local: "C:/Users/carde/Desktop/MUACK/herramientas_gestion/orca"
    categoria_operativa: "canibalizacion_logica"
    lenguaje_principal: "Python / TypeScript"
    descripcion_tecnica: "Motor para ejecucion paralela y sincronizacion de subagentes independientes."
    modulos_a_canibalizar:
      - utilidad: "Mecanismo de memoria compartida y arbitraje de conflictos entre resultados de subagentes concurrentes."
    accion_agente: "Extraer la logica de resolucion de tareas paralelas para aplicarla en el auditor de conceptos multiples."

  - id: "vibe-trading"
    nombre: "Vibe-Trading Agent"
    ruta_local: "C:/Users/carde/Desktop/MUACK/herramientas_gestion/Vibe-Trading"
    categoria_operativa: "canibalizacion_logica"
    lenguaje_principal: "Python"
    descripcion_tecnica: "Agente cuantitativo con bucle de evaluacion de riesgo y toma de decisiones probabilistica."
    modulos_a_canibalizar:
      - utilidad: "El bucle de evaluacion de reglas de umbral de riesgo (Stop-Loss / Validacion estricta)."
    accion_agente: "Reutilizar su bucle de toma de decisiones para calificar el nivel de riesgo financiero de una obra publica."

  - id: "x-algorithm"
    nombre: "X Recommendation Algorithm"
    ruta_local: "C:/Users/carde/Desktop/MUACK/herramientas_gestion/x-algorithm"
    categoria_operativa: "canibalizacion_logica"
    lenguaje_principal: "Scala / Rust / Java"
    descripcion_tecnica: "Algoritmo de puntuacion y ranking de candidatos a gran escala."
    modulos_a_canibalizar:
      - concepto: "Formulas del 'Heavy Ranker' adaptadas para clasificar expedientes municipales por orden de criticidad o sospecha de anomalia."
    accion_agente: "Extraer la ponderacion matematica y traducirla a una funcion pura en Python."

  - id: "reverse-skill"
    nombre: "Reverse Engineering Agent Skills"
    ruta_local: "C:/Users/carde/Desktop/MUACK/herramientas_gestion/reverse-skill"
    categoria_operativa: "canibalizacion_logica"
    lenguaje_principal: "Python"
    descripcion_tecnica: "Conjunto de habilidades agenticas para desensamblado e inspeccion forense de archivos binarios."
    modulos_a_canibalizar:
      - utilidad: "Rutinas de inspeccion de firmas hexadecimales de archivos y deteccion de malware en adjuntos."
    accion_agente: "Copiar las funciones de deteccion de extensiones y firmas magicas en la capa de carga de archivos."

  - id: "claude-ads"
    nombre: "Claude Ads Operations"
    ruta_local: "C:/Users/carde/Desktop/MUACK/herramientas_gestion/claude-ads"
    categoria_operativa: "canibalizacion_logica"
    lenguaje_principal: "Python"
    descripcion_tecnica: "Sistema de analisis y alertas ante anomalias de metricas."
    modulos_a_canibalizar:
      - utilidad: "Detectores de anomalias en series de tiempo y desviacion de presupuesto."
    accion_agente: "Adaptar los detectores de desviacion presupuestal para alertar sobrecostos en conceptos de obra."

  - id: "toprank"
    nombre: "TopRank Web & SEO Auditor"
    ruta_local: "C:/Users/carde/Desktop/MUACK/herramientas_gestion/toprank"
    categoria_operativa: "canibalizacion_logica"
    lenguaje_principal: "Python / Node.js"
    descripcion_tecnica: "Evaluador de metricas de rendimiento web y auditoria tecnica de accesibilidad."
    modulos_a_canibalizar:
      - utilidad: "Generadores de reportes con estructura de semaforo (rojo/amarillo/verde)."
    accion_agente: "Extraer las plantillas de reporte de hallazgos periciales para el generador de PDFs de SIGEDI."

  - id: "torlink"
    nombre: "TorLink Secure Proxy"
    ruta_local: "C:/Users/carde/Desktop/MUACK/herramientas_gestion/torlink"
    categoria_operativa: "canibalizacion_logica"
    lenguaje_principal: "Python / C"
    descripcion_tecnica: "Libreria de tuneles cifrados y sockets SOCKS5 para transmision segura de datos."
    modulos_a_canibalizar:
      - utilidad: "Configuracion de conexiones cifradas seguras punto a punto."
    accion_agente: "Copiar configuraciones de proxy si se requiere conectar con un servidor remoto protegido."

  # ============================================================================
  # 5. DIRECTORIOS DE REFERENCIA Y RECURSOS
  # ============================================================================

  - id: "free-for-dev"
    nombre: "Free for Developers Catalog"
    ruta_local: "C:/Users/carde/Desktop/MUACK/herramientas_gestion/free-for-dev"
    categoria_operativa: "referencia_recursos"
    lenguaje_principal: "Markdown"
    descripcion_tecnica: "Directorio exhaustivo de infraestructura gratuita en la nube (Postgres, Redis, Storage, Hosting)."
    accion_agente: "Consultar cuando se requiera aprovisionar un servicio en la nube gratuito (ej. Upstash Redis, Neon Postgres, Resend Email) sin costo."

---
# FIN DE ESPECIFICACION DETERMINISTA
