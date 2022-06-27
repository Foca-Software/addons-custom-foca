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
    "version": "13.0.0.1.1",
    "development_status": "Production/Stable",
    "application": False,
    "installable": True,
    "depends": [
        "web",
        "debo_integration_fields",
        "debo_cc_session_states",
        "debo_fuel_cash_control_moves",
        "fuel_tanks_cash_control",
        "debo_fuel_tanks",
    ],
    "qweb": [
        "static/src/xml/product_sales_list_widget_template.xml",
        "static/src/xml/fuel_detailed_list_widget_template.xml",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizard/cc_spreadsheet_cards_details_wizard.xml",
        "wizard/cc_spreadsheet_checks_wizard.xml",
        "wizard/cc_spreadsheet_complement_invoices_wizard.xml",
        "wizard/cc_spreadsheet_oil_card_invoices_wizard.xml",
        "wizard/cc_spreadsheet_other_dispatches_wizard.xml",
        "wizard/cc_spreadsheet_other_sales_oil_companies_wizard.xml",
        "wizard/cc_spreadsheet_partial_withdrawals_wizard.xml",
        "views/cash_control_session_views.xml",
        "views/cash_control_session_spreadsheet_assets.xml",
        "views/cash_control_session_spreadsheet_views.xml",
    ],
}
