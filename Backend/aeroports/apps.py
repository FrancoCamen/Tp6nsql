# backend/aeropuertos/apps.py
from django.apps import AppConfig

class AeropuertosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'aeropuertos'

    def ready(self):
        print("Inicializando la aplicación aeropuertos...")
        #import os
        #from django.conf import settings
        #from utils.load_airport_data import load_airport_data

        #if os.getenv('RUN_INITIAL_LOAD', 'false').lower() == 'true':
        #    print("Ejecutando carga inicial de datos...")
        #    json_path = os.path.join(settings.BASE_DIR, 'data_transport.json')
        #    load_airport_data(json_path)
        #else:
        #    print("Carga inicial desactivada (RUN_INITIAL_LOAD=false).")
