import csv
from django.core.management.base import BaseCommand
from recipes.models import Ingredients, MeasureUnits


class Command(BaseCommand):
    help = 'Импортировать ингредиенты из CSV файла'

    def handle(self, *args, **options):
        file_path = 'data/ingredients.csv'
        with open(file_path, 'r', encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file)
            next(csv_reader)

            for row in csv_reader:
                name, measurement_unit_name = row[0], row[1]

                measurement_unit, created = MeasureUnits.objects.get_or_create(
                    name=measurement_unit_name)

                ingredient = Ingredients.objects.create(
                    name=name,
                    measurement_unit=measurement_unit
                )
                ingredient.save()

        self.stdout.write(self.style.SUCCESS('Ингредиенты успешно '
                                             'импортированы в базу данных'))
