import { useEffect, useRef, useState } from 'react'
import mapboxgl from 'mapbox-gl'
import 'mapbox-gl/dist/mapbox-gl.css'
import './App.css'

mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_TOKEN

// Centros de apoyo en Tampico y Ciudad Madero
var CENTROS_APOYO = [
  {
    id: 'terminal-tampico',
    nombre: 'Terminal de Autobuses de Tampico',
    direccion: 'Blvd. Adolfo Lopez Mateos s/n, Col. Unidad Nacional, Tampico, Tam.',
    telefono: '833 213 5757',
    capacidad: '400 personas',
    servicios: 'Agua, alimentos, primeros auxilios, sanitarios',
    estado: 'Activo',
    coordenadas: [-97.8728, 22.2170]
  },
  {
    id: 'auditorio-tampico',
    nombre: 'Auditorio Municipal de Tampico',
    direccion: 'Blvd. Adolfo Lopez Mateos, Tampico, Tam.',
    telefono: '833 212 0000',
    capacidad: '800 personas',
    servicios: 'Agua, alimentos, refugio temporal, atencion medica',
    estado: 'Activo',
    coordenadas: [-97.8610, 22.2330]
  },
  {
    id: 'tecnologico-madero',
    nombre: 'Instituto Tecnologico de Cd. Madero',
    direccion: 'Av. 1o. de Mayo esq. Sor Juana Ines de la Cruz, Cd. Madero, Tam.',
    telefono: '833 357 4820',
    capacidad: '600 personas',
    servicios: 'Agua, alimentos, refugio, comunicaciones',
    estado: 'Activo',
    coordenadas: [-97.8364, 22.2756]
  }
]

function calcularDistanciaHaversine(lat1, lon1, lat2, lon2) {
  var R = 6371
  var dLat = (lat2 - lat1) * Math.PI / 180
  var dLon = (lon2 - lon1) * Math.PI / 180
  var a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
    Math.sin(dLon / 2) * Math.sin(dLon / 2)
  var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
  return R * c
}

function generarPopupCentro(centro) {
  return [
    '<div style="font-family: Inter, sans-serif; max-width: 250px; color: #07090E;">',
    '<h3 style="margin:0 0 6px; color:#F59E0B; font-size:14px;">' + centro.nombre + '</h3>',
    '<p style="margin:0 0 4px; font-size:12px;">' + centro.direccion + '</p>',
    '<p style="margin:0 0 4px; font-size:12px;">Tel: ' + centro.telefono + '</p>',
    '<p style="margin:0 0 4px; font-size:12px; font-weight:bold;">Capacidad: ' + centro.capacidad + '</p>',
    '<p style="margin:0 0 4px; font-size:12px;">Servicios: ' + centro.servicios + '</p>',
    '<p style="margin:0; font-size:12px; color:green; font-weight:bold;">Estado: ' + centro.estado + '</p>',
    '</div>'
  ].join('')
}

function App() {
  var contenedorMapa = useRef(null)
  var instanciaMapa = useRef(null)
  var marcadorUsuario = useRef(null)
  var [ubicacionUsuario, setUbicacionUsuario] = useState(null)
  var [error, setError] = useState(null)
  var [cargando, setCargando] = useState(true)
  var [infoRuta, setInfoRuta] = useState(null)

  // Inicializar mapa Mapbox
  useEffect(function () {
    if (instanciaMapa.current) return

    var mapa = new mapboxgl.Map({
      container: contenedorMapa.current,
      style: 'mapbox://styles/mapbox/streets-v12',
      center: [-97.8614, 22.2476], // Centro de Tampico
      zoom: 13
    })

    instanciaMapa.current = mapa

    mapa.on('load', function () {
      setCargando(false)

      // Colocar marcadores de los centros de apoyo
      CENTROS_APOYO.forEach(function (centro) {
        new mapboxgl.Marker({ color: '#F59E0B' })
          .setLngLat(centro.coordenadas)
          .setPopup(new mapboxgl.Popup({ offset: 25, maxWidth: '280px' }).setHTML(generarPopupCentro(centro)))
          .addTo(mapa)
      })
    })

    return function () {
      if (instanciaMapa.current) {
        instanciaMapa.current.remove()
        instanciaMapa.current = null
      }
    }
  }, [])

  // Trazar ruta entre dos puntos via OSRM
  function trazarRutaOSRM(origenLng, origenLat, destinoLng, destinoLat) {
    var mapa = instanciaMapa.current
    if (!mapa) return

    var url = 'https://router.project-osrm.org/route/v1/driving/' +
      origenLng + ',' + origenLat + ';' +
      destinoLng + ',' + destinoLat +
      '?overview=full&geometries=geojson'

    fetch(url)
      .then(function (res) { return res.json() })
      .then(function (datos) {
        if (!datos.routes || datos.routes.length === 0) {
          setError('No se encontro ruta disponible.')
          return
        }

        var ruta = datos.routes[0]
        var distanciaKm = (ruta.distance / 1000).toFixed(1)
        var duracionMin = Math.ceil(ruta.duration / 60)

        setInfoRuta({
          distancia: distanciaKm + ' km',
          duracion: duracionMin + ' min'
        })

        var geojsonData = {
          type: 'Feature',
          properties: {},
          geometry: ruta.geometry
        }

        // Si ya existe la fuente, actualizar datos
        if (mapa.getSource('ruta-source')) {
          mapa.getSource('ruta-source').setData(geojsonData)
        } else {
          mapa.addSource('ruta-source', {
            type: 'geojson',
            data: geojsonData
          })

          mapa.addLayer({
            id: 'ruta-linea',
            type: 'line',
            source: 'ruta-source',
            layout: {
              'line-join': 'round',
              'line-cap': 'round'
            },
            paint: {
              'line-color': '#e11d48',
              'line-width': 5,
              'line-opacity': 0.85
            }
          })
        }

        // Encuadrar ambos puntos
        var limites = new mapboxgl.LngLatBounds()
        limites.extend([origenLng, origenLat])
        limites.extend([destinoLng, destinoLat])
        mapa.fitBounds(limites, { padding: 80 })
      })
      .catch(function (err) {
        console.error('Error OSRM:', err)
        setError('Error de red al calcular la ruta.')
      })
  }

  // Obtener ubicacion del usuario y trazar ruta al centro mas cercano
  function obtenerUbicacionYTrazarRuta() {
    if (!navigator.geolocation) {
      setError('Geolocalizacion no soportada en este navegador.')
      return
    }

    var mapa = instanciaMapa.current
    if (!mapa) {
      setError('El mapa aun no esta listo.')
      return
    }

    setError(null)
    setInfoRuta(null)

    navigator.geolocation.getCurrentPosition(
      function (posicion) {
        var lat = posicion.coords.latitude
        var lng = posicion.coords.longitude
        setUbicacionUsuario({ latitude: lat, longitude: lng })

        // Remover marcador anterior del usuario si existe
        if (marcadorUsuario.current) {
          marcadorUsuario.current.remove()
        }

        // Colocar marcador del usuario
        marcadorUsuario.current = new mapboxgl.Marker({ color: '#3b82f6' })
          .setLngLat([lng, lat])
          .setPopup(new mapboxgl.Popup({ offset: 25 }).setHTML(
            '<div style="font-family:Inter,sans-serif;color:#07090E;">' +
            '<h3 style="margin:0 0 4px;color:#3b82f6;font-size:14px;">Tu ubicacion</h3>' +
            '<p style="margin:0;font-size:12px;">' + lat.toFixed(6) + ', ' + lng.toFixed(6) + '</p>' +
            '</div>'
          ))
          .addTo(mapa)

        // Encontrar centro de apoyo mas cercano por Haversine
        var indiceMasCercano = 0
        var distanciaMinima = Infinity

        for (var i = 0; i < CENTROS_APOYO.length; i++) {
          var centro = CENTROS_APOYO[i]
          var dist = calcularDistanciaHaversine(
            lat, lng,
            centro.coordenadas[1], centro.coordenadas[0]
          )
          if (dist < distanciaMinima) {
            distanciaMinima = dist
            indiceMasCercano = i
          }
        }

        var destino = CENTROS_APOYO[indiceMasCercano]

        // Trazar ruta via OSRM al mas cercano
        trazarRutaOSRM(lng, lat, destino.coordenadas[0], destino.coordenadas[1])
      },
      function (err) {
        setError('Error al obtener ubicacion: ' + err.message)
      },
      {
        enableHighAccuracy: true,
        timeout: 15000,
        maximumAge: 0
      }
    )
  }

  return (
    <div className="app">
      <div ref={contenedorMapa} className="map-container" />
      <div className="controls">
        <button onClick={obtenerUbicacionYTrazarRuta} disabled={cargando}>
          {cargando ? 'Cargando mapa...' : 'Trazar Ruta al Centro de Apoyo'}
        </button>
        {error && <p className="error">{error}</p>}
        {ubicacionUsuario && (
          <p className="location">
            Tu posicion: {ubicacionUsuario.latitude.toFixed(4)}, {ubicacionUsuario.longitude.toFixed(4)}
          </p>
        )}
        {infoRuta && (
          <div className="info-ruta">
            <strong>Ruta calculada:</strong> {infoRuta.distancia} - {infoRuta.duracion} aprox.
          </div>
        )}
      </div>
    </div>
  )
}

export default App
