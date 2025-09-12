import json
import os
from django.core.management.base import BaseCommand
from api.models import Ingredient


class Command(BaseCommand):
    help = 'Load ingredients from JSON file'

    def handle(self, *args, **options):
        file_path = os.path.join('data', 'ingredients.json')

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                ingredients_data = json.load(f)

            count = 0
            for item in ingredients_data:
                if (isinstance(item, dict) and 'name' in item
                        and 'measurement_unit' in item):
                    ingredient, created = Ingredient.objects.get_or_create(
                        name=item['name'],
                        measurement_unit=item['measurement_unit']
                    )
                    if created:
                        count += 1

            self.stdout.write(
                self.style.SUCCESS(f'Successfully loaded {count} ingredients')
            )

        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f'File {file_path} not found')
            )
        except json.JSONDecodeError:
            self.stdout.write(
                self.style.ERROR(f'Invalid JSON format in {file_path}')
            )
