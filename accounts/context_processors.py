from .permissions import can_access_module


def sidebar_permissions(request):
    user = request.user

    return {
        "can_view_dashboard": can_access_module(user, "dashboard"),
        "can_view_accounts": can_access_module(user, "accounts"),
        "can_view_categories": can_access_module(user, "categories"),
        "can_view_customers": can_access_module(user, "customers"),
        "can_view_inventory": can_access_module(user, "inventory"),
        "can_view_processing": can_access_module(user, "processing"),
        "can_view_orders": can_access_module(user, "orders"),
        "can_view_production": can_access_module(user, "production"),
        "can_view_packing": can_access_module(user, "packing"),
        "can_view_transport": can_access_module(user, "transport"),
        "can_view_hr": can_access_module(user, "hr"),
        "can_view_finance": can_access_module(user, "finance"),
        "can_view_reports": can_access_module(user, "reports"),
    }