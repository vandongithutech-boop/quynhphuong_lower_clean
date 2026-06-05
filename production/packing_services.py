import math

from .models import PackingBox,PackingBoxItem,PackingStemRule,ProductPackingRule,BoxCapacity


from .models import (
    PackingBox,
    PackingBoxItem,
    PackingStemRule,
    BoxCapacity,
)


def auto_generate_packing(
    production_order,
    selected_rule_ids=None,
    box_type_id=None,
):
    production_order.boxes.all().delete()

    if not selected_rule_ids:
        return production_order

    stem_rules = (
        PackingStemRule.objects
        .filter(id__in=selected_rule_ids)
        .order_by("-stems_quantity")
    )

    selected_box = None

    if box_type_id:
        selected_box = BoxCapacity.objects.filter(id=box_type_id).first()

    box_number = 1

    for item in production_order.items.all():
        remaining_stems = float(item.required_quantity or 0)

        if remaining_stems <= 0:
            continue

        for rule in stem_rules:
            stems_per_bunch = float(rule.stems_quantity or 0)

            if stems_per_bunch <= 0:
                continue

            if remaining_stems <= 0:
                break

            bunches = int(remaining_stems // stems_per_bunch)

            if bunches <= 0:
                continue

            total_stems = bunches * stems_per_bunch

            nw = round(total_stems * 0.008, 2)

            gw = round(
                nw + (selected_box.box_weight if selected_box else 1.4),
                2
            )

            box_code = (
                f"{production_order.production_code}"
                f"-{selected_box.code if selected_box else 'BOX'}"
                f"-{box_number:03d}"
            )

            box = PackingBox.objects.create(
                production_order=production_order,
                box_code=box_code,
                box_number=box_number,
                total_bunches=bunches,
                total_stems=total_stems,
                nw=nw,
                gw=gw,
            )

            PackingBoxItem.objects.create(
                box=box,
                production_item=item,
                product_code=item.product_code,
                product_name=item.product_name,
                bunches=bunches,
                stems=total_stems,
                stems_per_bunch=stems_per_bunch,
                nw=nw,
                gw=gw,
            )

            remaining_stems -= total_stems

            box_number += 1

    production_order.status = "packing"
    production_order.save()

    return production_order