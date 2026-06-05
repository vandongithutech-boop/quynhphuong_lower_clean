from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction

from inventory.models import InventoryTransaction


class Command(BaseCommand):
    help = "Bù tồn đầu kỳ cho các dòng báo cáo đang bị tồn đầu âm theo ngày nghiệp vụ"

    def add_arguments(self, parser):
        parser.add_argument(
            "--report-date",
            required=True,
            help="Ngày báo cáo đang bị âm tồn đầu, dạng YYYY-MM-DD"
        )

        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Chỉ xem trước, chưa tạo giao dịch"
        )

    def handle(self, *args, **options):
        report_date = timezone.datetime.strptime(
            options["report_date"],
            "%Y-%m-%d"
        ).date()

        dry_run = options.get("dry_run")

        before_transactions = InventoryTransaction.objects.filter(
            business_date__lt=report_date
        )

        def clean_text(value):
            return str(value or "").strip()

        def clean_grade(value):
            value = str(value or "").strip().lower()
            if value in ["", "-", "none", "null", "chưa có dữ liệu"]:
                return ""
            return value

        def make_key(trans):
            return (
                clean_text(trans.warehouse_type),
                clean_text(trans.product_group),
                clean_text(trans.product_code),
                clean_text(trans.product_name),
                clean_text(trans.unit),
                clean_grade(trans.flower_grade),
            )

        rows = {}

        for trans in before_transactions:
            key = make_key(trans)

            if key not in rows:
                rows[key] = {
                    "sample": trans,
                    "opening_qty": 0,
                }

            qty = float(trans.quantity or 0)

            if trans.transaction_type == "IN":
                rows[key]["opening_qty"] += abs(qty)

            elif trans.transaction_type == "OUT":
                rows[key]["opening_qty"] -= abs(qty)

            elif trans.transaction_type in ["CHECK", "ADJUST", "TRANSFER"]:
                rows[key]["opening_qty"] += qty

        need_fix = []

        for key, data in rows.items():
            opening_qty = data["opening_qty"]

            if opening_qty < 0:
                need_fix.append((key, data, abs(opening_qty)))

        if not need_fix:
            self.stdout.write(
                self.style.SUCCESS("Không còn dòng tồn đầu âm cần xử lý.")
            )
            return

        self.stdout.write(
            self.style.WARNING(
                f"Tìm thấy {len(need_fix)} dòng tồn đầu âm cần bù."
            )
        )

        with transaction.atomic():
            for key, data, fix_qty in need_fix:
                sample = data["sample"]

                self.stdout.write(
                    f"{sample.warehouse_type} | {sample.product_code} | "
                    f"{sample.product_name} | {sample.flower_grade or '-'} | "
                    f"Tồn đầu âm={data['opening_qty']:g} | Cần bù={fix_qty:g}"
                )

                if dry_run:
                    continue

                existed = InventoryTransaction.objects.filter(
                    transaction_type="ADJUST",
                    reference_code="FIX-NEGATIVE-OPENING",
                    business_date=report_date,
                    warehouse_type=sample.warehouse_type,
                    product_group=sample.product_group,
                    product_code=sample.product_code,
                    product_name=sample.product_name,
                    unit=sample.unit,
                    flower_grade=sample.flower_grade or "",
                ).exists()

                if existed:
                    continue

                InventoryTransaction.objects.create(
                    lot=sample.lot,
                    transaction_code=f"FIXOPEN{timezone.now().strftime('%Y%m%d%H%M%S%f')}",
                    transaction_type="ADJUST",
                    warehouse_type=sample.warehouse_type,
                    product_group=sample.product_group,
                    product_code=sample.product_code,
                    product_name=sample.product_name,
                    unit=sample.unit or "-",
                    flower_grade=sample.flower_grade or "",
                    supplier_code=sample.supplier_code or "",
                    supplier_name=sample.supplier_name or "-",
                    received_date=sample.received_date,
                    quantity=fix_qty,
                    reference_code="FIX-NEGATIVE-OPENING",
                    business_date=report_date,
                    note=(
                        f"Bù tồn đầu âm trên báo cáo ngày {report_date}. "
                        f"Tồn đầu trước khi bù: {data['opening_qty']:g}. "
                        f"Số bù: {fix_qty:g}."
                    ),
                )

        if dry_run:
            self.stdout.write(
                self.style.WARNING("Dry-run: chưa tạo giao dịch nào.")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS("Hoàn tất bù các dòng tồn đầu âm.")
            )