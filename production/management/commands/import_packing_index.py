from django.core.management.base import BaseCommand
from categories.models import FlowerType
from production.models import PackingIndex


PACKING_INDEX_DATA = [
    ("DÂU", "New Pink Rose", 1),
    ("HỶ TRỨNG", "Jumilia Rose", 1.2),
    ("SEN ĐẠI", "Sweet Memory Rose", 1.2),
    ("VÀNG CHÙA", "Big Yellow Rose", 1),
    ("VÀNG HELLEN", "Momentum Rose", 1),
    ("OHARA HỒNG", "Pink O’hara Rose", 1.2),
    ("CAM SPIRIT", "Free Spirit Rose", 1.2),
    ("ĐỎ ỚT", "Chilli Red Rose", 1.3),
    ("SHIMMER", "Shimmer Rose", 0.8),
    ("TRẮNG Ù", "Big White Rose", 1.2),
    ("HỘT GÀ", "Peach Avalanche Rose", 1.2),
    ("ĐỎ ECUADOR", "Red Ecuador Rose", 1),
    ("PINK FLOYD", "Pink Floyd Rose", 1),
    ("CAM HELLEN", "Hellen Rose", 1.2),
    ("HỒNG LUÂN ĐÔN", "Pink X-Pression Rose", 1),
    ("CHÙM CÁNH DÀI", "Spray Chrys Yellow", 1.2),
    ("CÚC CHÙM VƯỜN", "Farm Spray Chrys", 1.3),
    ("CÁT TƯỜNG THƯỜNG", "Lisianthus", 1.2),
    ("MÕM SÓI", "Snapdragon", 1),
    ("SALEM TRẮNG", "White Salem", 1),
    ("BABY TRẮNG", "Gypsophila", 1.3),
    ("BABY HỒNG", "Pink Gypsophila", 1.3),
    ("ĐỒNG TIỀN", "Gerbera", 0.8),
    ("CẨM CHƯỚNG", "Carnation", 0.8),
    ("THỦY TIÊN", "Daffodil", 1),
    ("CÚC MẪU ĐƠN", "Ping Pong", 1),
    ("LAN TƯỜNG", "Orchid", 1.5),
    ("LÁ BẠC", "", 0.3),
    ("LÁ CHANH", "", 0.25),
    ("EUCALYPTUS", "", 0.3),
    ("SONG HỶ", "", 0.16),
    ("PHỤ KIỆN MIX", "", 0.2),
    ("SALEM TÍM", "", 1),
    ("SALEM HỒNG", "", 1),
    ("CÚC CALIMERO", "", 1),
    ("THẠCH THẢO", "", 0.8),
]


class Command(BaseCommand):
    help = "Import chỉ số đóng thùng vào PackingIndex"

    def handle(self, *args, **kwargs):
        created_count = 0
        updated_count = 0
        not_found = []

        for vi_name, export_name, index_value in PACKING_INDEX_DATA:
            flower = (
                FlowerType.objects.filter(name__iexact=vi_name).first()
                or FlowerType.objects.filter(name__icontains=vi_name).first()
            )

            if not flower and export_name:
                flower = FlowerType.objects.filter(export_name__icontains=export_name).first()

            if not flower:
                not_found.append(vi_name)
                continue

            obj, created = PackingIndex.objects.update_or_create(
                flower=flower,
                defaults={
                    "packing_index": index_value,
                    "base_stems": 50,
                    "is_active": True,
                    "note": f"Import từ dữ liệu Packing Index: {vi_name} / {export_name}",
                }
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(self.style.SUCCESS(f"Tạo mới: {created_count}"))
        self.stdout.write(self.style.SUCCESS(f"Cập nhật: {updated_count}"))

        if not_found:
            self.stdout.write(self.style.WARNING("Không tìm thấy trong FlowerType:"))
            for name in not_found:
                self.stdout.write(f"- {name}")