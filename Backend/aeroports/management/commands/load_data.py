# project_name/your_app/management/commands/load_airport_data.py
from django.core.management.base import BaseCommand
from aeroports.utils.load_airport_data import load_airport_data

class Command(BaseCommand):
    help = 'Carga datos de aeropuertos desde un archivo JSON hacia MongoDB y Redis'

    def add_arguments(self, parser):
        parser.add_argument('json_file', nargs='?', type=str, default='data_transport.json')

    def handle(self, *args, **options):
        json_file_path = options['json_file']
        self.stdout.write(f"Cargando datos de aeropuertos desde {json_file_path}")
        load_airport_data(json_file_path)
        self.stdout.write(self.style.SUCCESS('Datos de aeropuertos cargados exitosamente'))