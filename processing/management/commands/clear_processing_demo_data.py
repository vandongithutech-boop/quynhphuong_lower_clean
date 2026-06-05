from django.core.management.base import BaseCommand
from django.db import transaction

from processing.models import (
    ProcessingTicket,
    ProcessingTicketItem,
    LooseStemStock,
    LooseStemMerge,
    LooseStemMergeItem,
)

from inventory.models import InventoryStock, InventoryTransaction


class Command(BaseCommand):
    help = "Xóa dữ liệu demo phần sơ chế và dữ liệu kho phát sinh từ sơ chế"

    def add_arguments(self, parser):
        parser.add_argument(
            "--confirm",
            action="store_true",
            help="Xác nhận xóa dữ liệu sơ chế"
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if not options["confirm"]:
            self.stdout.write(
                self.style.WARNING(
                    "\nLệnh này sẽ xóa dữ liệu demo phần sơ chế:\n"
                    "- Phiếu sơ chế\n"
                    "- Chi tiết phiếu sơ chế\n"
                    "- Khay cành lẻ\n"
                    "- Phiếu ghép cành lẻ\n"
                    "- Giao dịch kho có mã tham chiếu bắt đầu bằng SC hoặc SCM\n"
                    "- Tồn kho hiện tại sẽ được xóa sạch để nhập lại tồn thực tế\n\n"
                    "Muốn chạy thật, dùng:\n"
                    "python manage.py clear_processing_demo_data --confirm\n"
                )
            )
            return

        delete_plan = [
            ("Chi tiết ghép cành lẻ", LooseStemMergeItem),
            ("Phiếu ghép cành lẻ", LooseStemMerge),
            ("Khay cành lẻ", LooseStemStock),
            ("Chi tiết phiếu sơ chế", ProcessingTicketItem),
            ("Phiếu sơ chế", ProcessingTicket),
        ]

        for label, model in delete_plan:
            count = model.objects.count()
            model.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f"Đã xóa {count} dòng: {label}"))

        trans_qs = InventoryTransaction.objects.filter(
            reference_code__regex=r"^(SC|SCM)"
        )
        trans_count = trans_qs.count()
        trans_qs.delete()
        self.stdout.write(
            self.style.SUCCESS(f"Đã xóa {trans_count} dòng lịch sử kho phát sinh từ sơ chế.")
        )

        stock_count = InventoryStock.objects.count()
        InventoryStock.objects.all().delete()
        self.stdout.write(
            self.style.SUCCESS(f"Đã xóa {stock_count} dòng tồn kho hiện tại để nhập lại tồn thực tế.")
        )

        self.stdout.write(
            self.style.SUCCESS(
                "\nHoàn tất. Đã dọn sạch dữ liệu sơ chế demo và tồn kho hiện tại.\n"
                "Bây giờ anh có thể kiểm kê/nhập lại tồn thực tế từ đầu."
            )
        )