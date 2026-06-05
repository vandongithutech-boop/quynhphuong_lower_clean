from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from production.models import PackingBoxItem
from inventory.models import InventoryTransaction


class Command(BaseCommand):
    help = "Tạo bù lịch sử OUT cho các thùng đóng gói đã trừ kho nhưng chưa ghi InventoryTransaction"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        created_count = 0
        skipped_count = 0

        box_items = (
            PackingBoxItem.objects
            .select_related(
                "box",
                "box__production_order",
                "lot",
                "production_item",
            )
            .order_by("created_at", "id")
        )

        for box_item in box_items:
            box = box_item.box
            production = box.production_order if box else None

            if not production:
                skipped_count += 1
                continue

            quantity = float(box_item.stems or 0)

            if quantity <= 0:
                skipped_count += 1
                continue

            existed = InventoryTransaction.objects.filter(
                transaction_type="OUT",
                reference_code=production.production_code,
                product_code=box_item.product_code,
                product_name=box_item.product_name,
                quantity=quantity,
                note__icontains=f"Thùng {box.box_code}",
            ).exists()

            if existed:
                skipped_count += 1
                continue

            product_group = ""
            unit = "cành"
            warehouse_type = "FINISHED"
            flower_grade = ""

            if box_item.production_item:
                unit = box_item.production_item.unit or "cành"

                flower_type = (
                    box_item.production_item.flower_type
                    or ""
                )

                if flower_type in ["HH", "HP", "VT"]:
                    product_group = flower_type

            if not product_group:
                if box_item.product_code and box_item.product_code.startswith("VT"):
                    product_group = "VT"
                else:
                    product_group = "HP"

            InventoryTransaction.objects.create(
                lot=box_item.lot,
                transaction_code=f"DG-BF{timezone.now().strftime('%Y%m%d%H%M%S%f')}",
                transaction_type="OUT",
                warehouse_type=warehouse_type,
                product_group=product_group,
                product_code=box_item.product_code or "-",
                product_name=box_item.product_name or "-",
                unit=unit,
                flower_grade=flower_grade,
                supplier_code="",
                supplier_name="-",
                received_date=None,
                quantity=quantity,
                reference_code=production.production_code,
                note=(
                    f"Backfill xuất kho do đóng gói sản xuất. "
                    f"Thùng {box.box_code} - Lệnh {production.production_code} - "
                    f"Đơn {production.order_code}"
                ),
                created_at=box_item.created_at,
            )

            created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Hoàn tất backfill. Tạo mới {created_count} giao dịch OUT, bỏ qua {skipped_count} dòng."
            )
        )