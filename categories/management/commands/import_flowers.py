import openpyxl
from django.core.management.base import BaseCommand
from categories.models import FlowerType


def clean_text(value):
    if value is None:
        return ""
    return str(value).strip()


class Command(BaseCommand):
    help = "Import loại hoa từ file Excel vào database"

    def add_arguments(self, parser):
        parser.add_argument("excel_file", type=str)

    def handle(self, *args, **kwargs):
        excel_file = kwargs["excel_file"]

        wb = openpyxl.load_workbook(excel_file, data_only=True)
        ws = wb["DM_HH"]

        count_create = 0
        count_update = 0

        for row in ws.iter_rows(min_row=2, values_only=True):
            code = clean_text(row[0])
            name = clean_text(row[1])

            if not code or not name:
                continue

            flower, created = FlowerType.objects.update_or_create(
                code=code,
                defaults={
                    "name": name,
                    "color": clean_text(row[2]),
                    "origin": clean_text(row[3]),
                    "stem_length": clean_text(row[4]),
                    "unit": clean_text(row[5]),
                    "processing_loss_rate": row[6] or 0,
                    "category_type": clean_text(row[7]),
                }
            )

            if created:
                count_create += 1
            else:
                count_update += 1

        self.stdout.write(self.style.SUCCESS(
            f"Import xong: thêm mới {count_create}, cập nhật {count_update}"
        ))