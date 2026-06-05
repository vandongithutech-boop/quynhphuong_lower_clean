import pandas as pd
from django.core.management.base import BaseCommand
from categories.models import Customer


class Command(BaseCommand):
    help = 'Import danh sách khách hàng từ file Excel'

    def handle(self, *args, **kwargs):
        file_path = 'data/DM_KH.xlsx'
        sheet_name = 'KH'

        df = pd.read_excel(file_path, sheet_name=sheet_name)

        # Xóa toàn bộ dữ liệu cũ (nếu muốn)
        # Customer.objects.all().delete()

        count = 0

        for _, row in df.iterrows():
            ma_kh = str(row.get('MÃ KH', '')).strip()

            if not ma_kh or ma_kh == 'nan':
                continue

            Customer.objects.update_or_create(
                ma_kh=ma_kh,
                defaults={
                    'ten_khach_hang': str(row.get('TÊN KHÁCH HÀNG', '')).strip(),
                    'dia_chi': str(row.get('ĐỊA CHỈ', '')).strip(),
                    'sdt': str(row.get('SĐT', '')).strip(),
                    'van_chuyen': str(row.get('VẬN CHUYỂN', '')).strip(),
                    'vung': str(row.get('VÙNG', '')).strip(),
                    'nguoi_nhan_thay': str(row.get('NGƯỜI NHẬN THAY ( NHÂN CPC)', '')).strip(),
                    'ma_dau': str(row.get('MÃ ĐẦU', '')).strip(),
                    'country': str(row.get('COUNTRY(V/N)', '')).strip(),
                    'phan_loai_kh': str(row.get('PHÂN LOẠI KH (C/M/L)', '')).strip(),
                    'ma_so_thue': str(row.get('MÃ SỐ THUẾ', '')).strip(),
                }
            )

            count += 1
            print(f'Đã import: {ma_kh}')

        self.stdout.write(
            self.style.SUCCESS(f'Import thành công {count} khách hàng.')
        )