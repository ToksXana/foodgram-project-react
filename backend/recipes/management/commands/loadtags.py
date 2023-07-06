import json

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Tags


class Command(BaseCommand):
    """Импорт тегов из json-file в db."""
    help = 'Импорт тегов из json-file в db'

    def handle(self, *args, **kwargs):
        data_path = settings.BASE_DIR
        with open(
            f'{data_path}/data/tags.json', 'r', encoding='utf-8'
        ) as jsonfile:
            data = json.load(jsonfile)
            for row in data:
                Tags.objects.create(name=row["name"],
                                    color=row["color"],
                                    slug=row["slug"])
        self.stdout.write('Теги загружены')
