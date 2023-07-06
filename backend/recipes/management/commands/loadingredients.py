import csv

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredients


class Command(BaseCommand):
    """Импорт ингредиентов из scv-file в db."""
    help = 'Импорт ингредиентов из scv-file в db'

    def handle(self, *args, **kwargs):
        data_path = settings.BASE_DIR
        with open(
            f'{data_path}/data/ingredients.csv', 'r', encoding='utf-8'
        ) as csvfile:
            data = csv.reader(csvfile)
            for row in data:
                Ingredients.objects.create(name=row[0],
                                           measurement_unit=row[1])
        self.stdout.write('Ингредиенты загружены')
