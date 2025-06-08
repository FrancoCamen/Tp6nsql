# project_name/utils/load_airport_data.py
import json
import os
from django.conf import settings
from .database_config import DatabaseConnections

def load_airport_data(json_file_path='data_transport.json'):
    """Carga datos de aeropuertos desde un archivo JSON hacia MongoDB y Redis."""
    # Inicializa conexiones a las bases de datos
    mongo_db = DatabaseConnections.get_mongo_client()
    redis_geo = DatabaseConnections.get_redis_geo()
    redis_popularity = DatabaseConnections.get_redis_popularity()

    # Limpia datos existentes en MongoDB y Redis GEO (opcional, comenta si no es necesario)
    mongo_db.airports.drop()
    redis_geo.flushdb()

    # Inicializa el conjunto de popularidad vacío con TTL de 1 día
    redis_popularity.flushdb()
    redis_popularity.expire('airport_popularity', 86400)

    # Carga datos JSON
    try:
        with open(json_file_path, encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        print(f"Error: No se encontró {json_file_path}")
        return
    except json.JSONDecodeError:
        print(f"Error: Formato JSON inválido en {json_file_path}")
        return

    # Contador para los aeropuertos cargados
    loaded_airports = 0

    for airport in data:
        # Obtiene iata_faa e icao, si existen
        iata_faa = airport.get('iata_faa')
        icao = airport.get('icao')

        # Si no tiene ni iata_faa ni icao, salta este aeropuerto
        if not iata_faa and not icao:
            continue

        # Inserta en MongoDB (colección airports) con todos los atributos
        mongo_db.airports.insert_one({
            'name': airport.get('name'),
            'city': airport.get('city'),
            'iata_faa': iata_faa,
            'icao': icao,
            'lat': airport.get('lat'),
            'lng': airport.get('lng'),
            'alt': airport.get('alt'),
            'tz': airport.get('tz')
        })

        # Usa iata_faa como identificador en Redis GEO si está presente, de lo contrario usa icao
        identifier = iata_faa if iata_faa else icao

        # Agrega a Redis GEO con GEOADD (usando lng, lat, y el identificador)
        redis_geo.geoadd(
            'airports_geo',
            (airport.get('lng'), airport.get('lat'), identifier)
        )

        loaded_airports += 1


    print(f"Se cargaron loaded_airports aeropuertos en MongoDB y Redis GEO")