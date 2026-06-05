from django.core.management.base import BaseCommand
from django.utils import timezone

from inventory.models import InventoryTransaction


class Command(BaseCommand):
    help = "Chỉnh ngày nghiệp vụ cho lịch sử kho theo khoảng thời gian tạo giao dịch"

    def add_arguments(self, parser):
        parser.add_argument(
            "--from-datetime",
            required=True,
            help="Thời gian bắt đầu, dạng YYYY-MM-DD HH:MM"
        )

        parser.add_argument(
            "--to-datetime",
            required=True,
            help="Thời gian kết thúc, dạng YYYY-MM-DD HH:MM"
        )

        parser.add_argument(
            "--business-date",
            required=True,
            help="Ngày nghiệp vụ cần gán, dạng YYYY-MM-DD"
        )

    def handle(self, *args, **options):
        current_tz = timezone.get_current_timezone()

        from_dt = timezone.datetime.strptime(
            options["from_datetime"],
            "%Y-%m-%d %H:%M"
        )

        to_dt = timezone.datetime.strptime(
            options["to_datetime"],
            "%Y-%m-%d %H:%M"
        )

        business_date = timezone.datetime.strptime(
            options["business_date"],
            "%Y-%m-%d"
        ).date()

        from_dt = timezone.make_aware(from_dt, current_tz)
        to_dt = timezone.make_aware(to_dt, current_tz)

        qs = InventoryTransaction.objects.filter(
            created_at__range=(from_dt, to_dt)
        )

        count = qs.count()

        self.stdout.write(
            f"Tìm thấy {count} giao dịch từ {from_dt} đến {to_dt}."
        )

        qs.update(business_date=business_date)

        self.stdout.write(
            self.style.SUCCESS(
                f"Đã cập nhật {count} giao dịch về ngày nghiệp vụ {business_date}."
            )
        )