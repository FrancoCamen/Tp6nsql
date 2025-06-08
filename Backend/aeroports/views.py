# backend/aeropuertos/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from .utils.database_config import DatabaseConnections
import json

@api_view(["POST", "GET"])
def airports(request):
        
    if request.method == 'GET':
        """
        GET /airports/
        Retorna una lista de todos los aeropuertos almacenados en MongoDB.
        """
        try:
            # Obtener el cliente de MongoDB
            mongo_db = DatabaseConnections.get_mongo_client()
            
            # Consultar todos los aeropuertos
            airports = list(mongo_db.airports.find({}, {'_id': 0}))  # Excluir el campo '_id'
            
            return JsonResponse({'airports': airports}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    if request.method == 'POST':
        """
        POST /airports/
        Crea un nuevo aeropuerto y lo guarda en MongoDB y Redis GEO.
        """
        if request.method != 'POST':
            return JsonResponse({'error': 'Método no permitido. Use POST.'}, status=405)

        try:
            data = json.loads(request.body.decode('utf-8'))
            required_fields = ['name', 'city', 'iata_faa', 'icao', 'lat', 'lng', 'alt', 'tz']
            if not all(field in data for field in required_fields):
                return JsonResponse({'error': 'Faltan campos requeridos'}, status=400)

            mongo_db = DatabaseConnections.get_mongo_client()
            redis_geo = DatabaseConnections.get_redis_geo()

            airport_data = {
                'name': data['name'],
                'city': data['city'],
                'iata_faa': data['iata_faa'],
                'icao': data['icao'],
                'lat': float(data['lat']),
                'lng': float(data['lng']),
                'alt': int(data['alt']),
                'tz': data['tz']
            }
            result = mongo_db.airports.insert_one(airport_data)  # Inserta y obtiene el resultado

            # Crear una copia del airport_data sin _id para la respuesta
            response_airport = airport_data.copy()
            if '_id' in response_airport:
                del response_airport['_id']

            identifier = data['iata_faa'] if data['iata_faa'] else data['icao']
            redis_geo.geoadd('airports_geo', (float(data['lng']), float(data['lat']), identifier))

            return JsonResponse({
                'message': 'Aeropuerto creado exitosamente',
                'airport': response_airport
            }, status=201)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Datos JSON inválidos'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
    
    
def get_popular_airports(request):
    """
    GET /airports/popular
    Retorna los 10 aeropuertos más populares según las visitas, junto con sus detalles.
    """
    try:
        # Obtener clientes de Redis y MongoDB
        redis_popularity = DatabaseConnections.get_redis_popularity()
        mongo_db = DatabaseConnections.get_mongo_client()

        # Obtener los 10 aeropuertos más populares (identificador y puntaje)
        popular_airports = redis_popularity.zrevrange('airport_popularity', 0, 9, withscores=True)

        # Si no hay aeropuertos populares, retornar lista vacía
        if not popular_airports:
            return JsonResponse({'popular_airports': []}, status=200)

        # Preparar lista para la respuesta
        result = []
        for identifier, score in popular_airports:
            # Buscar el aeropuerto en MongoDB usando iata_faa o icao
            airport = mongo_db.airports.find_one(
                {'$or': [{'iata_faa': identifier}, {'icao': identifier}]},
                {'_id': 0}
            )
            if airport:
                # Agregar el puntaje de popularidad al diccionario del aeropuerto
                airport['popularity_score'] = score
                result.append(airport)

        return JsonResponse({'popular_airports': result}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@api_view(["GET", "PUT", "DELETE"])
def airport_by_iata(request, iata_code):
        
    if request.method == 'GET':
        """
        GET /airports/{iata_code}
        Retorna los datos de un aeropuerto y suma 1 a su popularidad en Redis.
        """
        try:
            mongo_db = DatabaseConnections.get_mongo_client()
            redis_popularity = DatabaseConnections.get_redis_popularity()

            # Consultar el aeropuerto en MongoDB por iata_faa o icao
            airport = mongo_db.airports.find_one(
                {'$or': [{'iata_faa': iata_code}, {'icao': iata_code}]},
                {'_id': 0}
            )
            if not airport:
                return JsonResponse({'error': 'Aeropuerto no encontrado'}, status=404)

            identifier = airport.get('iata_faa', airport.get('icao'))
            redis_popularity.zincrby('airport_popularity', 1, identifier)

            # Establecer TTL de 1 día (86,400 segundos) en la clave airport_popularity
            redis_popularity.expire('airport_popularity', 86400)

            return JsonResponse({
                'message': 'Datos del aeropuerto retornados y popularidad actualizada',
                'airport': airport
            }, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    if request.method == 'PUT':
        """
        PUT /airports/{iata_code}
        Modifica los datos de un aeropuerto existente en MongoDB.
        """
        if request.method != 'PUT':
            return JsonResponse({'error': 'Método no permitido. Use PUT.'}, status=405)

        try:
            # Parsear el cuerpo de la solicitud como JSON
            data = json.loads(request.body.decode('utf-8'))
            
            # Campos permitidos para actualización (todos son opcionales)
            update_fields = ['name', 'city', 'lat', 'lng', 'alt', 'tz']
            update_data = {key: value for key, value in data.items() if key in update_fields}

            # Validar tipos si se proporcionan
            if 'lat' in update_data:
                update_data['lat'] = float(update_data['lat'])
            if 'lng' in update_data:
                update_data['lng'] = float(update_data['lng'])
            if 'alt' in update_data:
                update_data['alt'] = int(update_data['alt'])

            mongo_db = DatabaseConnections.get_mongo_client()

            # Buscar y actualizar el aeropuerto
            airport = mongo_db.airports.find_one_and_update(
                {'$or': [{'iata_faa': iata_code}, {'icao': iata_code}]},
                {'$set': update_data},
                return_document=True,
                projection={'_id': 0}
            )

            if not airport:
                return JsonResponse({'error': 'Aeropuerto no encontrado'}, status=404)

            return JsonResponse({
                'message': 'Aeropuerto actualizado exitosamente',
                'airport': airport
            }, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Datos JSON inválidos'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
    if request.method == 'DELETE':
        """
        DELETE /airports/{iata_code}
        Elimina un aeropuerto de MongoDB, Redis GEO y Redis Popularidad.
        """
        if request.method != 'DELETE':
            return JsonResponse({'error': 'Método no permitido. Use DELETE.'}, status=405)

        try:
            mongo_db = DatabaseConnections.get_mongo_client()
            redis_geo = DatabaseConnections.get_redis_geo()
            redis_popularity = DatabaseConnections.get_redis_popularity()

            # Buscar el aeropuerto para obtener el identificador correcto
            airport = mongo_db.airports.find_one(
                {'$or': [{'iata_faa': iata_code}, {'icao': iata_code}]},
                {'_id': 0, 'iata_faa': 1, 'icao': 1}
            )
            if not airport:
                return JsonResponse({'error': 'Aeropuerto no encontrado'}, status=404)

            # Determinar el identificador (iata_faa preferido, sino icao)
            identifier = airport.get('iata_faa', airport.get('icao'))

            # Eliminar del conjunto GEO en Redis
            redis_geo.zrem('airports_geo', identifier)

            # Eliminar la entrada de popularidad en Redis
            redis_popularity.zrem('airport_popularity', identifier)

            # Eliminar del MongoDB
            result = mongo_db.airports.delete_one(
                {'$or': [{'iata_faa': iata_code}, {'icao': iata_code}]}
            )

            if result.deleted_count == 0:
                return JsonResponse({'error': 'No se pudo eliminar el aeropuerto'}, status=500)

            return JsonResponse({
                'message': 'Aeropuerto eliminado exitosamente'
            }, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@api_view(["GET"])   
def get_nearby_airports(request):
    """
    GET /airports/nearby?lat=...&lng=...&radius=...km
    Busca aeropuertos cercanos usando GEORADIUS en Redis.
    """
    try:
        # Obtener parámetros de la solicitud
        lat = request.GET.get('lat')
        lng = request.GET.get('lng')
        radius = request.GET.get('radius')

        if not all([lat, lng, radius]):
            return JsonResponse({'error': 'Faltan parámetros (lat, lng, radius)'}, status=400)

        # Convertir a tipos adecuados
        lat = float(lat)
        lng = float(lng)
        radius = float(radius)  # Radio en kilómetros

        mongo_db = DatabaseConnections.get_mongo_client()
        redis_geo = DatabaseConnections.get_redis_geo()

        # Consultar Redis GEO con GEORADIUS
        nearby_airports = redis_geo.georadius(
            'airports_geo',
            lng,
            lat,
            radius,
            unit='km',
            withdist=True,
            withcoord=False
        )

        if not nearby_airports:
            return JsonResponse({'nearby_airports': []}, status=200)

        # Obtener detalles de los aeropuertos desde MongoDB
        result = []
        for identifier, distance in nearby_airports:
            airport = mongo_db.airports.find_one(
                {'$or': [{'iata_faa': identifier}, {'icao': identifier}]},
                {'_id': 0}
            )
            if airport:
                airport['distance_km'] = float(distance)  # Convertir distancia a float
                result.append(airport)

        return JsonResponse({
            'nearby_airports': result
        }, status=200)
    except ValueError:
        return JsonResponse({'error': 'Parámetros inválidos (deben ser numéricos)'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

