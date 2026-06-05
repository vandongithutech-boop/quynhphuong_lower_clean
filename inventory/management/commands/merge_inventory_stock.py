from django.core.management.base import BaseCommand
from django.db import transaction

from inventory.models import InventoryStock


class Command(BaseCommand):
    help = "Gộp tồn kho thật trong DB theo kho + nhóm + mã sản phẩm + loại/độ hoa đã chuẩn hóa"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        def clean_grade(value):
            value = str(value or "").strip().lower()

            if value in ["", "-", "none", "null", "chưa có dữ liệu"]:
                return ""

            return value

        def make_key(stock):
            return (
                stock.warehouse_type or "",
                stock.product_group or "",
                stock.product_code or "",
                clean_grade(stock.flower_grade),
            )

        stocks = list(
            InventoryStock.objects
            .select_for_update()
            .order_by("warehouse_type", "product_group", "product_code", "id")
        )

        groups = {}

        for stock in stocks:
            key = make_key(stock)

            if key not in groups:
                groups[key] = []

            groups[key].append(stock)

        merged_count = 0
        deleted_count = 0

        for key, group_stocks in groups.items():
            if len(group_stocks) <= 1:
                stock = group_stocks[0]

                cleaned_grade = clean_grade(stock.flower_grade)
                changed = False

                if (stock.flower_grade or "") != cleaned_grade:
                    stock.flower_grade = cleaned_grade
                    changed = True

                if stock.supplier_code is None:
                    stock.supplier_code = ""
                    changed = True

                if stock.supplier_name in [None, ""]:
                    stock.supplier_name = "-"
                    changed = True

                if changed:
                    stock.save()

                continue

            canonical = None

            for stock in group_stocks:
                if (stock.supplier_code in ["", None]) and stock.received_date is None:
                    canonical = stock
                    break

            if canonical is None:
                canonical = group_stocks[0]

            total_quantity = sum(float(s.quantity or 0) for s in group_stocks)

            latest_info = group_stocks[-1]

            other_ids = [
                s.id for s in group_stocks
                if s.id != canonical.id
            ]

            InventoryStock.objects.filter(id__in=other_ids).delete()

            canonical.quantity = total_quantity
            canonical.flower_grade = clean_grade(canonical.flower_grade)
            canonical.supplier_code = ""
            canonical.supplier_name = "-"
            canonical.received_date = None

            canonical.product_name = latest_info.product_name or canonical.product_name
            canonical.unit = latest_info.unit or canonical.unit

            if not canonical.lot and latest_info.lot:
                canonical.lot = latest_info.lot

            canonical.save()

            merged_count += 1
            deleted_count += len(other_ids)

            self.stdout.write(
                self.style.SUCCESS(
                    f"Đã gộp {len(group_stocks)} dòng: "
                    f"{canonical.warehouse_type} | {canonical.product_group} | "
                    f"{canonical.product_code} | {canonical.product_name} = {canonical.quantity:g}"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Hoàn tất. Gộp {merged_count} nhóm, xóa {deleted_count} dòng tách."
            )
        )