from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = "Xóa sạch dữ liệu nhập vào: kho tổng, sơ chế, đơn hàng, sản xuất/đóng gói"

    def add_arguments(self, parser):
        parser.add_argument(
            "--confirm",
            action="store_true",
            help="Xác nhận xóa dữ liệu"
        )

        parser.add_argument(
            "--yes-i-know",
            action="store_true",
            help="Xác nhận lần 2 để tránh chạy nhầm"
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if not options["confirm"] or not options["yes_i_know"]:
            self.stdout.write(
                self.style.WARNING(
                    "\nLỆNH NÀY SẼ XÓA SẠCH DỮ LIỆU VẬN HÀNH:\n"
                    "- Kho tổng / nhập kho / xuất kho / tồn kho / lịch sử kho\n"
                    "- Sơ chế / chi tiết sơ chế / cành lẻ / ghép cành lẻ\n"
                    "- Đơn hàng / chi tiết đơn hàng\n"
                    "- Sản xuất / chi tiết sản xuất / thùng đóng gói\n\n"
                    "KHÔNG XÓA:\n"
                    "- Tài khoản đăng nhập\n"
                    "- Nhân viên\n"
                    "- Danh mục sản phẩm / loại hoa\n"
                    "- Nhà cung cấp\n"
                    "- Quy cách đóng gói / loại thùng\n"
                    "- Phân quyền / cài đặt hệ thống\n\n"
                    "Muốn chạy thật, dùng:\n"
                    "python manage.py reset_operational_data --confirm --yes-i-know\n"
                )
            )
            return

        from inventory.models import (
            InventoryStock,
            InventoryTransaction,
            InventoryReceipt,
            InventoryReceiptItem,
            InventoryStockOut,
            InventoryStockOutItem,
        )

        from processing.models import (
            ProcessingTicket,
            ProcessingTicketItem,
            LooseStemStock,
            LooseStemMerge,
            LooseStemMergeItem,
        )

        from orders.models import (
            Order,
            OrderItem,
        )

        from production.models import (
            ProductionOrder,
            ProductionItem,
            PackingBox,
            PackingBoxItem,
        )

        delete_plan = [
            # Sản xuất / đóng gói
            ("Chi tiết thùng đóng gói", PackingBoxItem),
            ("Thùng đóng gói", PackingBox),
            ("Chi tiết lệnh sản xuất", ProductionItem),
            ("Lệnh sản xuất", ProductionOrder),

            # Đơn hàng
            ("Chi tiết đơn hàng", OrderItem),
            ("Đơn hàng", Order),

            # Sơ chế
            ("Chi tiết ghép cành lẻ", LooseStemMergeItem),
            ("Phiếu ghép cành lẻ", LooseStemMerge),
            ("Khay cành lẻ", LooseStemStock),
            ("Chi tiết phiếu sơ chế", ProcessingTicketItem),
            ("Phiếu sơ chế", ProcessingTicket),

            # Kho tổng
            ("Chi tiết phiếu xuất kho", InventoryStockOutItem),
            ("Phiếu xuất kho", InventoryStockOut),
            ("Chi tiết phiếu nhập kho", InventoryReceiptItem),
            ("Phiếu nhập kho", InventoryReceipt),
            ("Lịch sử kho", InventoryTransaction),
            ("Tồn kho", InventoryStock),
        ]

        self.stdout.write(self.style.WARNING("\nBẮT ĐẦU XÓA DỮ LIỆU VẬN HÀNH...\n"))

        for label, model in delete_plan:
            count = model.objects.count()
            model.objects.all().delete()

            self.stdout.write(
                self.style.SUCCESS(
                    f"Đã xóa {count} dòng: {label}"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                "\nHOÀN TẤT. Dữ liệu kho tổng, sơ chế, đơn hàng và sản xuất đã sạch.\n"
                "Dữ liệu nền như tài khoản, nhân viên, danh mục sản phẩm, nhà cung cấp vẫn được giữ lại.\n"
            )
        )