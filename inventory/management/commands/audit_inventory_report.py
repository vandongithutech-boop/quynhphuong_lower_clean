from django.core.management.base import BaseCommand
from django.db.models import Sum

from inventory.models import InventoryStock, InventoryTransaction


class Command(BaseCommand):
    help = "Đối soát tồn kho hiện tại với lịch sử giao dịch để tìm dòng âm/sai"

    def add_arguments(self, parser):
        parser.add_argument("--product-code", required=False, help="Lọc theo mã sản phẩm")
        parser.add_argument("--warehouse", required=False, help="Lọc theo kho")
        parser.add_argument("--only-negative", action="store_true", help="Chỉ hiện dòng âm theo transaction")

    def handle(self, *args, **options):
        product_code = options.get("product_code")
        warehouse = options.get("warehouse")
        only_negative = options.get("only_negative")

        transactions = InventoryTransaction.objects.all()

        if product_code:
            transactions = transactions.filter(product_code=product_code)

        if warehouse:
            transactions = transactions.filter(warehouse_type=warehouse)

        report = {}

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

        for trans in transactions:
            key = key_of(trans)

            if key not in report:
                report[key] = {
                    "in": 0,
                    "out": 0,
                    "check": 0,
                    "balance": 0,
                    "current_stock": 0,
                }

            qty = float(trans.quantity or 0)

            if trans.transaction_type == "IN":
                report[key]["in"] += abs(qty)
                report[key]["balance"] += abs(qty)

            elif trans.transaction_type == "OUT":
                report[key]["out"] += abs(qty)
                report[key]["balance"] -= abs(qty)

            elif trans.transaction_type in ["CHECK", "ADJUST", "TRANSFER"]:
                report[key]["check"] += qty
                report[key]["balance"] += qty

        stocks = InventoryStock.objects.all()

        if product_code:
            stocks = stocks.filter(product_code=product_code)

        if warehouse:
            stocks = stocks.filter(warehouse_type=warehouse)

        for stock in stocks:
            key = key_of(stock)

            if key not in report:
                report[key] = {
                    "in": 0,
                    "out": 0,
                    "check": 0,
                    "balance": 0,
                    "current_stock": 0,
                }

            report[key]["current_stock"] += float(stock.quantity or 0)

        rows = []

        for key, data in report.items():
            warehouse_type, product_group, code, name, unit, grade = key
            balance = data["balance"]
            current_stock = data["current_stock"]
            diff = current_stock - balance

            if only_negative and balance >= 0 and current_stock >= 0:
                continue

            rows.append({
                "warehouse": warehouse_type,
                "group": product_group,
                "code": code,
                "name": name,
                "unit": unit,
                "grade": grade or "-",
                "in": data["in"],
                "out": data["out"],
                "check": data["check"],
                "balance": balance,
                "current_stock": current_stock,
                "diff": diff,
            })

        rows.sort(key=lambda x: (x["warehouse"], x["name"], x["grade"]))

        for row in rows:
            if row["balance"] < 0 or row["current_stock"] < 0 or row["diff"] != 0:
                self.stdout.write(
                    f"{row['warehouse']} | {row['code']} | {row['name']} | {row['grade']} | "
                    f"IN={row['in']:g} OUT={row['out']:g} CHECK={row['check']:g} | "
                    f"THEO GD={row['balance']:g} | KHO HIỆN TẠI={row['current_stock']:g} | LỆCH={row['diff']:g}"
                )

        self.stdout.write(self.style.SUCCESS("Hoàn tất đối soát."))