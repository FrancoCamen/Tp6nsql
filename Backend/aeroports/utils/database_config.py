# backend/utils/database_config.py
from pymongo import MongoClient
import redis
import os
from django.conf import settings

class DatabaseConnections:
    @staticmethod
    def get_mongo_client():
        """Inicializa y retorna el cliente de MongoDB con autenticación."""
        mongo_uri = os.getenv('MONGO_URI', 'mongodb://admin:admin123@localhost:27017/?authSource=admin')
        try:
            client = MongoClient(mongo_uri)
            # Verifica la conexión ping
            client.admin.command('ping')
            print("Conexión a MongoDB establecida correctamente.")
            return client[settings.MONGO_DB_NAME]
        except Exception as e:
            print(f"Error al conectar a MongoDB: {e}")
            raise

    @staticmethod
    def get_redis_geo():
        """Inicializa y retorna el cliente de Redis para GEO (base de datos 4)."""
        redis_host = os.getenv('REDIS_HOST', 'localhost')
        redis_port = int(os.getenv('REDIS_PORT', 6379))
        try:
            redis_client = redis.Redis(host=redis_host, port=redis_port, db=4, decode_responses=True)
            # Verifica la conexión ping
            redis_client.ping()
            print("Conexión a Redis GEO (db 4) establecida correctamente.")
            return redis_client
        except Exception as e:
            print(f"Error al conectar a Redis GEO: {e}")
            raise

    @staticmethod
    def get_redis_popularity():
        """Inicializa y retorna el cliente de Redis para popularidad (base de datos 5)."""
        redis_host = os.getenv('REDIS_HOST', 'localhost')
        redis_port = int(os.getenv('REDIS_PORT', 6379))
        try:
            redis_client = redis.Redis(host=redis_host, port=redis_port, db=5, decode_responses=True)
            # Verifica la conexión ping
            redis_client.ping()
            print("Conexión a Redis Popularidad (db 5) establecida correctamente.")
            return redis_client
        except Exception as e:
            print(f"Error al conectar a Redis Popularidad: {e}")
            raise