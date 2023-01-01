# Copyright 2019-21 ForgeFlow, S.L.
{
    "name": "Stock Picking Select Items By Location",
    "summary": "Stock Picking Select Items By Location",
    "version": "15.0.1.0.0",
    "category": "Warehouse Management",
    "license": "AGPL-3",
    "depends": ["product", "stock"],
    "data": [
        "security/ir.model.access.csv",
        "wizards/stock_report_quantity_by_location_views.xml",
        "views/stock_picking_view.xml",
    ],
    "installable": True,
}
