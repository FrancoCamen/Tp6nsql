#!/usr/bin/env python
import os
import sys

def main():
    # Configurar el módulo de settings antes de cualquier acceso
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aeroports.settings')
    try:
        from django.conf import settings
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "No se pudo importar Django. ¿Está instalado y "
            "disponible en su PYTHONPATH?"
        ) from exc

    print("Ejecutando carga inicial de datos...")
    # Ejecutar la carga inicial si está habilitada
    if os.getenv('RUN_INITIAL_LOAD', 'false').lower() == 'true':
        print("Ejecutando carga inicial de datos...")
        try:
            from aeroports.utils.load_airport_data import load_airport_data
            json_path = os.path.join(settings.BASE_DIR, 'data_transport.json')
            load_airport_data(json_path)
        except Exception as e:
            print(f"Error durante la carga inicial: {e}")
            sys.exit(1)

    # Continuar con la ejecución normal de Django
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
