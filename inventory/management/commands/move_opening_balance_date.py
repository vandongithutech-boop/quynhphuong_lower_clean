from django.core.management.base import BaseCommand
from django.utils import timezone

from inventory.models import InventoryTransaction


class Command(BaseCommand):
    help = "Chuyển ngày nghiệp vụ của các giao dịch tồn đầu kỳ"

    def add_arguments(self, parser):
        parser.add_argument(
            "--from-date",
            required=True,
            help="Ngày nghiệp vụ hiện tại đang sai, dạng YYYY-MM-DD"
        )
        parser.add_argument(
            "--to-date",
            required=True,
            help="Ngày nghiệp vụ đúng cần chuyển về, dạng YYYY-MM-DD"
        )
        parser.add_argument(
            "--reference-code",
            default="OPENING-BALANCE",
            help="Mã tham chiếu cần chuyển"
        )

    def handle(self, *args, **options):
        from_date = timezone.datetime.strptime(
            options["from_date"],
            "%Y-%m-%d"
        ).date()

        to_date = timezone.datetime.strptime(
            options["to_date"],
            "%Y-%m-%d"
        ).date()

        reference_code = options["reference_code"]

        qs = InventoryTransaction.objects.filter(
            transaction_type="ADJUST",
            reference_code=reference_code,
            business_date=from_date,
        )

        count = qs.count()

        self.stdout.write(
            f"Tìm thấy {count} giao dịch {reference_code} đang ở ngày {from_date}."
        )

        qs.update(business_date=to_date)

        self.stdout.write(
            self.style.SUCCESS(
                f"Đã chuyển {count} giao dịch {reference_code} từ {from_date} về {to_date}."
            )
        )