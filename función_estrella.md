**A ver, la cuestión es así: Se supone que la plataforma ofrece 2 aspectos para los usuarios.
Un grupo de usuarios son los que tienen acceso a la plataforma de modo administrativa,
mientras que otro grupo de usuarios son los que tienen acceso a la plataforma de modo de usuario final.


El usuario final sensible es aquel que debe estar informado de la información que se transmite a través de la plataforma
EL SaaS B2G, *'SIGRAS' Es un Sistema Inteligente de Gestión de rutas seguras para la población civil.* (nombre largo real)
Cuenta con una dashboard y con un mapa (cuenta con MapBox y con conexión a modelos de Ia para que mediante
el uso de tool_calling para que el modelo pueda construir sobre el mapa en base a ciertos datos que vaya recibiendo del lado 
administrativo, datos que ya han recabado de los usuarios civiles no adm.)

Objetivo General: Desarrollar un sistema de alertas para la ciudadanía
en situación de vulnerabilidad durante desastres naturales, con el fin de agilizar
la localización de centros de ayuda y rutas de movilidad, auxiliar a los centros de
acopio en el control de sus suministros y capacidad de alojamiento, e identificar
zonas de riesgo a través de reportes ciudadanos en tiempo real.
Definición:
Durante la ocurrencia de desastres naturales, las poblaciones en situación de vulnerabilidad
enfrentan graves barreras para acceder a asistencia inmediata, rutas seguras y refugio temporal.
Esta problemática se origina por la fragmentación de la información en tiempo real, la saturación
de las líneas de emergencia tradicionales y la falta de canales centralizados de comunicación entre
la ciudadanía y los organismos de auxilio.

# pantalla del usuario final sensible y funcionalidad
La primera pantalla en desempeñarse será la del usuario final sensible, donde se mostrará la información más relevante
y actualizada sobre las rutas seguras y los centros de ayuda disponibles en el área afectada por el desastre. En dos secciones que
no son dependientes la una de la otra; la priemra sección mostrará las rutas seguras y la segunda sección mostrará los centros de
ayuda disponibles en el área afectada por el desastre. en palabras más simples, una mostrará el mapa donde encontrará los centros
de ayuda y albergues más cercano aunado a las incidencias y casos de riesgos visibles en el mapa con su información. 
Y la segunda será donde pueda -sin iniciar sesión - su respectivo reporte y folio, sus detalles del problema y como se comparte
con el resto de la aplicación y los directivos para que puedan gestionar el problema y resolverlo lo antes posible. Delegarlo a la comitiva
de protección civil más cercana y adecuada. 

> Como requerimiento, incluir el permiso de geolocalización del usuario final sensible en el navegador.
> utilizar api mapbox u otro método para calcular la distancia entre el usuario final sensible y los centros de ayuda, omitiendo 
> en caso de haberlo, otras diversas zonas de riesgo
--  vas a recibir 2 parámetros del usuario en función del mapa: la localización del teléfono usando longitud y latitud.
Nosotros debemos devolverle al frontend la ruta más cercana evadiento zonas de riesgo anteriormente mostradas.  
> Que la primera sección sea la del mapa y cálculo de rutas, incidencias y por supuesto, centros de apoyo. 


[¡URGENTE] Asignarle una ruta a la api, su procesamiento lógico y el adaptador/cliente respectivo.**

