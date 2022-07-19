from odoo.http import request
from datetime import datetime

DEBO_DATE_FORMAT = "%d/%m/%Y"
ADMIN_ID = 2

def create_sale_order(user_id: int, line_data: dict) -> object or False:
    """
    Return list of sale.order object
    """
    sale_obj = request.env["sale.order"].with_user(user_id)
    sale_data = _get_sale_data()
    sale_order = sale_obj.create(sale_data)
    sale_order._add_lines([line_data])
    sale_order.compute_warehouse_id()
    sale_order.action_confirm()
    return sale_order


def _get_pump_test_partner_id() -> int:
    return request.env.ref("api_sale.debo_pump_test_partner").id


def _get_sale_data() -> str:
    sale_data = {
        "partner_id": _get_pump_test_partner_id(),
        "date_order": datetime.now(),
        "debo_transaction_type" : "pump_test"
    }
    return sale_data


def create_invoice_from_sale(sale_order: object) -> object:
    invoice_ids = sale_order._create_invoices()
    for invoice in invoice_ids:
        invoice.journal_id = _get_pump_test_journal_id()
        invoice.debo_transaction_type = "pump_test"
        remove_taxes(invoice)
    return invoice_ids

def remove_taxes(invoice: object):  
    for line in invoice.invoice_line_ids:
        if line.price_unit == 0 or invoice.amount_total < 0:
            line.tax_ids = [(5,0,0)]
            invoice.amount_total = 0

def unreserve_orders(sale_orders: object) -> object:
    picking_ids = (
        request.env["stock.picking"]
        .with_user(ADMIN_ID)
        .search([("sale_id", "in", sale_orders.ids)])
    )
    for picking in picking_ids:
            picking.do_unreserve()
    return picking_ids

def _get_pump_test_journal_id() -> int:
    return request.env.ref("api_sale.debo_pump_test_journal").id

def get_session_id(spreadsheet:str,store_id:int):
    session_obj = request.env['cash.control.session'].with_user(ADMIN_ID)
    session_id = session_obj.get_session_by_id_debo(spreadsheet,store_id)
    return session_id