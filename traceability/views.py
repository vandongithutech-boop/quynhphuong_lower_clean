from django.shortcuts import render, get_object_or_404
from .models import TraceLot
from production.models import PackingBox


def trace_lot_detail(request, lot_code):
    lot = get_object_or_404(TraceLot, lot_code=lot_code)

    logs = lot.logs.all().order_by("created_at")

    return render(request, "traceability/trace_lot_detail.html", {
        "lot": lot,
        "logs": logs,
    })

def trace_box_detail(request, box_id):
    box = get_object_or_404(
        PackingBox.objects.select_related(
            "production_order",
            "production_order__order",
            "box_type",
        ).prefetch_related(
            "items",
            "items__lot",
        ),
        id=box_id
    )

    return render(request, "traceability/trace_box_detail.html", {
        "box": box,
        "production": box.production_order,
        "order": box.production_order.order,
        "items": box.items.all(),
    })