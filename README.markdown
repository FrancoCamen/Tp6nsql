# Proyecto Aeropuertos

Este proyecto es una aplicación full-stack para gestionar información de aeropuertos. Incluye un backend basado en Django con MongoDB y Redis, y un frontend basado en HTML, CSS y JavaScript con Leaflet para visualizar aeropuertos en un mapa. Usa Docker Compose para simplificar la configuración y despliegue.

## Requisitos

- Docker
- Docker Compose
- Conexión a internet (para descargar imágenes y dependencias)

## Instalación y Levantamiento

1. **Clonar el repositorio**:

   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd <NOMBRE_DEL_REPOSITORIO>
   ```

2. **Levantar los servicios con Docker Compose**:

   ```bash
   docker-compose up --build
   ```

   - Esto construirá e iniciará los contenedores para el backend (puerto 8000), frontend (puerto 8080), MongoDB (puerto 27017) y Redis (puerto 6379).
   - El backend cargará datos iniciales automáticamente si `data_transport.json` está en la carpeta `backend`.

3. **Verificar el funcionamiento**:

   - Abre un navegador y ve a `http://localhost:8080` para el frontend.
   - Usa `http://localhost:8000` para interactuar con la API directamente (por ejemplo, con `curl` o Postman).

## Estructura del Proyecto

- `backend/`: Contiene el código Django, incluyendo vistas y configuraciones para MongoDB y Redis.
- `airport-frontend/`: Contiene el frontend con HTML, CSS y JavaScript, usando Leaflet y Leaflet.markercluster.
- `docker-compose.yml`: Define los servicios de Docker para backend, frontend, MongoDB y Redis.
- `README.md`: Este archivo.

## Funcionamiento

### Backend

El backend ofrece una API RESTful para gestionar aeropuertos:

- **Base URL**: `http://localhost:8000`

- **Endpoints**:

  - `GET /airports/`: Lista todos los aeropuertos.
  - `POST /airports/`: Crea un nuevo aeropuerto (requiere JSON con `name`, `city`, `iata_faa`, `icao`, `lat`, `lng`, `alt`, `tz`).
  - `GET /airports/<str:iata_code>/`: Obtiene datos de un aeropuerto y aumenta su popularidad (expira en 1 día).
  - `PUT /airports/<str:iata_code>/`: Actualiza datos de un aeropuerto.
  - `DELETE /airports/<str:iata_code>/`: Elimina un aeropuerto de todas las bases.
  - `GET /airports/popular/`: Lista los 10 aeropuertos más populares.
  - `GET /airports/nearby/?lat=...&lng=...&radius=...km`: Busca aeropuertos cercanos.

- **Tecnologías**:

  - Django como framework.
  - MongoDB para almacenamiento de datos.
  - Redis para popularidad (con TTL de 1 día por aeropuerto) y geolocalización.

### Frontend

El frontend muestra un mapa interactivo:

- **URL**: `http://localhost:8080`
- **Funcionalidades**:
  - Muestra todos los aeropuertos como marcadores en un mapa usando Leaflet.
  - Usa Leaflet.markercluster para agrupar marcadores cuando hay muchos.
  - Al hacer clic en un marcador, envía un `GET /airports/<iata_code>/` al backend, muestra un popup con los datos y actualiza la popularidad.
- **Tecnologías**:
  - HTML, CSS y JavaScript puro.
  - Leaflet para el mapa.
  - Leaflet.markercluster para clustering.

## Uso

1. **Explorar el mapa**:

   - Ve a `http://localhost:8080` y haz clic en los marcadores para ver detalles de los aeropuertos.
   - Los marcadores se agrupan automáticamente cuando el zoom es bajo.

2. **Probar la API**:

   - Usa herramientas como `curl` o Postman. Ejemplos:
     - Listar aeropuertos: `curl http://localhost:8000/airports/`
     - Obtener aeropuerto: `curl http://localhost:8000/airports/GKA/`
     - Crear aeropuerto: `curl -X POST -H "Content-Type: application/json" -d '{"name": "Nuevo", "city": "Ciudad", "iata_faa": "NUE", "icao": "NICA", "lat": -34.6, "lng": -58.4, "alt": 25, "tz": "America/Argentina/Buenos_Aires"}' http://localhost:8000/airports/`

3. **Detener los servicios**:

   ```bash
   docker-compose down
   ```

## Notas

- Asegúrate de que `data_transport.json` esté en la carpeta `backend` para cargar datos iniciales.
- Si hay problemas de CORS, configura el backend con `django-cors-headers` para permitir `http://localhost:8080`.
- La popularidad de cada aeropuerto expira después de 1 día sin visitas.

## 