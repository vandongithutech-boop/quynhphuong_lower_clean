import openpyxl
from django.core.management.base import BaseCommand
from employees.models import Employee


def clean_text(value):
    if value is None:
        return ""
    return str(value).strip()


def get_cell(row, index):
    if index < len(row):
        return row[index]
    return None


class Command(BaseCommand):
    help = "Import nhân sự từ file Excel vào database"

    def add_arguments(self, parser):
        parser.add_argument("excel_file", type=str)

    def handle(self, *args, **kwargs):
        excel_file = kwargs["excel_file"]

        wb = openpyxl.load_workbook(excel_file, data_only=True)
        ws = wb["nv"]

        count_create = 0
        count_update = 0
        count_skip = 0

        for row in ws.iter_rows(min_row=2, values_only=True):
            ma_nv = clean_text(get_cell(row, 0))
            ho_ten = clean_text(get_cell(row, 1))

            if not ma_nv or not ho_ten:
                count_skip += 1
                continue

            employee, created = Employee.objects.update_or_create(
                ma_nv=ma_nv,
                defaults={
                    "ho_ten": ho_ten,
                    "gioi_tinh": clean_text(get_cell(row, 2)),
                    "sdt": clean_text(get_cell(row, 3)),
                    "bo_phan": clean_text(get_cell(row, 4)),
                    "chuc_vu": clean_text(get_cell(row, 5)),
                    "dia_chi": clean_text(get_cell(row, 6)),
                    "ngay_vao_lam": get_cell(row, 7),
                    "trang_thai": clean_text(get_cell(row, 8)) or "Đang làm",
                    "ghi_chu": clean_text(get_cell(row, 9)),
                }
            )

            if created:
                count_create += 1
            else:
                count_update += 1

        self.stdout.write(self.style.SUCCESS(
            f"Import xong: thêm mới {count_create}, cập nhật {count_update}, bỏ qua {count_skip}"
        ))