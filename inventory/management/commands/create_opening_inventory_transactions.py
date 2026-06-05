from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from inventory.models import InventoryStock, InventoryTransaction


class Command(BaseCommand):
    help = "Tạo giao dịch tồn đầu kỳ để cân bằng InventoryStock hiện tại với lịch sử InventoryTransaction"

    def add_arguments(self, parser):
        parser.add_argument(
            "--business-date",
            required=True,
            help="Ngày nghiệp vụ ghi nhận tồn đầu kỳ, dạng YYYY-MM-DD"
        )

        parser.add_argument(
            "--product-code",
            required=False,
            help="Chỉ xử lý một mã sản phẩm"
        )

        parser.add_argument(
            "--warehouse",
            required=False,
            help="Chỉ xử lý một kho: RAW, FINISHED, SALE, MATERIAL, DAMAGED"
        )

        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Chỉ xem trước, chưa tạo dữ liệu"
        )

    def handle(self, *args, **options):
        business_date = timezone.datetime.strptime(
            options["business_date"],
            "%Y-%m-%d"
        ).date()

        product_code_filter = options.get("product_code")
        warehouse_filter = options.get("warehouse")
        dry_run = options.get("dry_run")

        def clean_grade(value):
            value = str(value or "").strip().lower()
            if value in ["", "-", "none", "null", "chưa có dữ liệu"]:
                return ""
            return value

        def key_of(obj):
            return (
                obj.warehouse_type or "",
                obj.product_group or "",
                obj.product_code or "",
                obj.product_name or "",
                obj.unit or "",
                clean_grade(obj.flower_grade),
            )

        stocks = InventoryStock.objects.all()

        if product_code_filter:
            stocks = stocks.filter(product_code=product_code_filter)

        if warehouse_filter:
            stocks = stocks.filter(warehouse_type=warehouse_filter)

        stock_map = {}

        for stock in stocks:
            key = key_of(stock)

            if key not in stock_map:
                stock_map[key] = {
                    "stock": stock,
                    "current_stock": 0,
                }

            stock_map[key]["current_stock"] += float(stock.quantity or 0)

        transactions_qs = InventoryTransaction.objects.all()

        if product_code_filter:
            transactions_qs = transactions_qs.filter(product_code=product_code_filter)

        if warehouse_filter:
            transactions_qs = transactions_qs.filter(warehouse_type=warehouse_filter)

        transaction_balance = {}

        for trans in transactions_qs:
            key = key_of(trans)

            if key not in transaction_balance:
                transaction_balance[key] = 0

            qty = float(trans.quantity or 0)

            if trans.transaction_type == "IN":
                transaction_balance[key] += abs(qty)

            elif trans.transaction_type == "OUT":
                transaction_balance[key] -= abs(qty)

            elif trans.transaction_type in ["CHECK", "ADJUST", "TRANSFER"]:
                transaction_balance[key] += qty

        created_count = 0
        skipped_count = 0

        with transaction.atomic():
            for key, data in stock_map.items():
                stock = data["stock"]
                current_stock = data["current_stock"]
                balance = transaction_balance.get(key, 0)

                diff = current_stock - balance

                if abs(diff) < 0.0001:
                    skipped_count += 1
                    continue

                existed = InventoryTransaction.objects.filter(
                    transaction_type="ADJUST",
                    reference_code="OPENING-BALANCE",
                    warehouse_type=stock.warehouse_type,
                    product_group=stock.product_group,
                    product_code=stock.product_code,
                    product_name=stock.product_name,
                    unit=stock.unit,
                    flower_grade=stock.flower_grade or "",
                ).exists()

                if existed:
                    skipped_count += 1
                    continue

                self.stdout.write(
                    f"{stock.warehouse_type} | {stock.product_code} | {stock.product_name} | "
                    f"Tồn kho={current_stock:g} | Theo GD={balance:g} | Cần bù={diff:g}"
                )

                if dry_run:
                    continue

                InventoryTransaction.objects.create(
                    lot=stock.lot,
                    transaction_code=f"OPEN{timezone.now().strftime('%Y%m%d%H%M%S%f')}",
                    transaction_type="ADJUST",
                    warehouse_type=stock.warehouse_type,
                    product_group=stock.product_group,
                    product_code=stock.product_code,
                    product_name=stock.product_name,
                    unit=stock.unit or "-",
                    flower_grade=stock.flower_grade or "",
                    supplier_code=stock.supplier_code or "",
                    supplier_name=stock.supplier_name or "-",
                    received_date=stock.received_date,
                    quantity=diff,
                    reference_code="OPENING-BALANCE",
                    business_date=business_date,
                    note=(
                        f"Tạo tồn đầu kỳ để cân bằng lịch sử giao dịch với tồn kho hiện tại. "
                        f"Tồn kho hiện tại: {current_stock:g}. "
                        f"Tồn theo giao dịch: {balance:g}. "
                        f"Số bù: {diff:g}."
                    ),
                )

                created_count += 1

        if dry_run:
            self.stdout.write(self.style.WARNING("Dry-run: chưa tạo giao dịch nào."))
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Hoàn tất. Đã tạo {created_count} giao dịch tồn đầu kỳ, bỏ qua {skipped_count} dòng."
                )
            )