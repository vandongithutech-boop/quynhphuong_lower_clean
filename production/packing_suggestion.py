from production.models import PackingIndex, BoxCapacity


def calculate_item_index(product_code, product_name, stems):
    packing = (
        PackingIndex.objects
        .filter(flower__code=product_code, is_active=True)
        .first()
    )

    if not packing:
        packing = (
            PackingIndex.objects
            .filter(flower__name__icontains=product_name, is_active=True)
            .first()
        )

    if not packing:
        return {
            "has_index": False,
            "packing_index": 0,
            "total_index": 0,
            "message": "Sản phẩm chưa có chỉ số đóng thùng."
        }

    base_stems = packing.base_stems or 50
    total_index = (float(stems) / float(base_stems)) * float(packing.packing_index)

    return {
        "has_index": True,
        "packing_index": packing.packing_index,
        "base_stems": base_stems,
        "total_index": round(total_index, 2),
        "message": ""
    }


def suggest_box_by_index(total_index):
    boxes = (
        BoxCapacity.objects
        .filter(is_active=True, capacity_index__gte=total_index)
        .order_by("capacity_index")
    )

    suggested_box = boxes.first()

    if suggested_box:
        return {
            "has_box": True,
            "box": suggested_box,
            "status": "PHÙ HỢP",
            "message": f"Gợi ý thùng {suggested_box.code}, sức chứa {suggested_box.capacity_index}."
        }

    largest_box = (
        BoxCapacity.objects
        .filter(is_active=True)
        .order_by("-capacity_index")
        .first()
    )

    if largest_box:
        return {
            "has_box": False,
            "box": largest_box,
            "status": "VƯỢT THÙNG",
            "message": f"Chỉ số vượt thùng lớn nhất {largest_box.code}. Cần tách thêm thùng."
        }

    return {
        "has_box": False,
        "box": None,
        "status": "CHƯA CÓ THÙNG",
        "message": "Chưa có dữ liệu sức chứa thùng."
    }


def build_packing_suggestion(product_code, product_name, stems):
    item_index = calculate_item_index(product_code, product_name, stems)

    if not item_index["has_index"]:
        return {
            **item_index,
            "box_code": "",
            "box_name": "",
            "box_capacity": 0,
            "status": "THỦ CÔNG",
        }

    box_suggestion = suggest_box_by_index(item_index["total_index"])
    box = box_suggestion["box"]

    return {
        **item_index,
        "box_code": box.code if box else "",
        "box_name": box.name if box else "",
        "box_capacity": box.capacity_index if box else 0,
        "box_weight": box.box_weight if box else 1.4,
        "status": box_suggestion["status"],
        "message": box_suggestion["message"],
    }

from production.models import PackingIndex, BoxCapacity


def calculate_box_total_index(box):
    total_index = 0

    for item in box.items.all():
        packing = (
            PackingIndex.objects
            .filter(flower__code=item.product_code, is_active=True)
            .first()
        )

        if not packing:
            packing = (
                PackingIndex.objects
                .filter(flower__name__icontains=item.product_name, is_active=True)
                .first()
            )

        if not packing:
            continue

        base_stems = packing.base_stems or 50
        item_index = (float(item.stems or 0) / float(base_stems)) * float(packing.packing_index or 0)

        total_index += item_index

    return round(total_index, 2)


def get_box_status(total_index, capacity_index):
    if capacity_index <= 0:
        return "CHƯA CÓ SỨC CHỨA"

    diff = capacity_index - total_index

    if diff < 0:
        return "THỪA"

    if diff <= 2:
        return "FULL"

    return "THIẾU"