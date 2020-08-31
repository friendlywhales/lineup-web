
import csv
import sys

from django.core.management.base import BaseCommand

from ... import models


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('path', type=str)

    def handle(self, *args, **options):
        csvpath = options['path']
        dialect = options.get('dialect', 'excel')
        delimiter = options.get('delimiter', ',')
        encoding = options.get('encoding', 'utf-8-sig')

        for item in self.load_csv(csvpath, dialect, delimiter, encoding):
            obj, is_created = models.PromotionCode.objects.get_or_create(
                value=item['code'],
                defaults={
                    'allow_quantity': item.get('allow_quantity', 1),
                    'expired_at': item.get('expired_at'),
                }
            )
            if not is_created:
                print(f'`{obj.value}` 은 이미 존재합니다.')
            else:
                extra_lineup_code = item.get('lineup_coin')
                if extra_lineup_code:
                    obj.extra['lineup_coin'] = extra_lineup_code
                    obj.save()
                print(f'`{obj.value}` 프로모션 코드를 등록했습니다.')

    @staticmethod
    def load_csv(path, dialect, delimiter, encoding):
        with open(path, 'r', encoding=encoding) as fp:
            rows = csv.DictReader(fp, delimiter=delimiter, dialect=dialect)
            try:
                for row in rows:
                    yield row
            except csv.Error as e:
                sys.exit(e.__str__())


