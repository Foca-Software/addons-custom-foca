# pylint: disable=missing-module-docstring,pointless-statement
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Debo Cash Control Session Spreadsheet",
    "summary": """
        This module adds the functionality to control the cash control session finalization with a spreadsheet.
    """,
    "author": "Calyx Servicios S.A.",
    "maintainers": ["FedericoGregori"],
    "website": "https://odoo.calyx-cloud.com.ar/",
    "license": "AGPL-3",
    "category": "Sales",
    "version": "13.0.0.0.3",
    "development_status": "Production/Stable",
    "application": False,
    "installable": True,
    "depends": [
        "web",
        "debo_integration_fields",
        "debo_cc_session_states",
        "fuel_tanks_cash_control",
    ],
    "qweb": [
        "static/src/xml/product_sales_list_widget_template.xml",
        "static/src/xml/fuel_detailed_list_widget_template.xml",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizard/cc_spreadsheet_partial_withdrawals_wizard.xml",
        "views/cash_control_session_views.xml",
        "views/cash_control_session_spreadsheet_assets.xml",
        "views/cash_control_session_spreadsheet_views.xml",
    ],
}
