import array
from odoo.http import request
from odoo import fields, http, api
from datetime import datetime
import logging
from odoo.exceptions import AccessError

_logger = logging.getLogger(__name__)

DEBO_DATE_FORMAT = "%d/%m/%Y"
ADMIN_ID = 2


def create_invoice(user_id: int, data: dict) -> dict:
    try:
        account_obj = request.env["account.move"].with_user(user_id)
        move_line_obj = request.env["account.move.line"].with_user(user_id)
    except AccessError as e:
        _logger.error(e.args)
        return {"invoice_id": 0, "status": "error", "error": e.args}
    invoice_data = data["header"]
    try:
        invoice_id = account_obj.create(
            {
                "partner_id": invoice_data["partner_id"],
                "partner_shipping_id": invoice_data["partner_shipping_id"],
                "ref": invoice_data["ref"],
                "invoice_date": datetime.strptime(
                    invoice_data["invoice_date"], DEBO_DATE_FORMAT
                ),
                "journal_id": invoice_data["journal_id"],
                "l10n_latam_document_type_id": invoice_data[
                    "l10n_latam_document_type_id"
                ],
                "company_id": invoice_data["company_id"],
                "currency_id": invoice_data["currency_id"],
                # not sent in the data
                "type": "out_invoice",
                "state": "draft",
            }
        )

    except ValueError as e:
        _logger.error(e.args)
        return {"invoice_id": 0, "status": "error", "error": e.args}
    try:
        created_invoice = account_obj.browse(invoice_id.id)
        for line in data["invoice_line_ids"]:
            created_invoice.invoice_line_ids = [
                (
                    0,
                    0,
                    {
                        "product_id": line["product_id"],
                        "name": line["name"],
                        "account_id": line["account_id"],
                        "quantity": line["quantity"],
                        "product_uom_id": line["product_uom_id"],
                        "price_unit": line["price_unit"],
                        "tax_ids": [(6, 0, [line["tax_ids"]])],
                        "exclude_from_invoice_tab": False,
                    },
                )
            ]
    except ValueError as e:
        _logger.error(e.args)
        return {
            "invoice_id": invoice_id.id,
            "status": "error",
            "message": "Error creating invoice",
        }

    return {
        "invoice_id": invoice_id.id,
        "status": "success",
        "message": "Invoice created successfully",
    }


def verify_user(user: str, password: str) -> int:
    user = (
        request.env["res.users"]
        .with_user(1)
        .search([("login", "=", user), ("password", "=", password)])
    )
    if user:
        return user.id
    else:
        return 0


def partner_exists(partner_id: int) -> bool:
    partner = request.env["res.partner"].with_user(1).search([("id", "=", partner_id)])
    if partner:
        return True
    else:
        return False


def check_required_fields(data: dict, move_type: int) -> list or False:
    """ """
    # move_type = str(move_type)
    required_fields = {
        101: [
            # "partner_id",
            # "partner_shipping_id",
            # "partner_invoice_id",
            "date_order",
            # "pricelist_id",
        ],
        102: [
            "partner_id",
            "partner_shipping_id",
            "ref",
            "invoice_date",
            "journal_id",
            "l10n_latam_document_type",
            "currency_id",
        ],
    }
    required_line_fields = {
        101: [
            "product_id",
            # "product_template_id",
            # "name",
            # "product_uom_qty",
            # "product_uom",
            # "price_unit",
            # "tax_id",
        ],
        102: [
            "product_id",
            "name",
            "account_id",
            "quantity",
            "product_uom_id",
            "price_unit",
            "tax_ids",
        ],
    }
    missing_fields = []
    for field in required_fields[move_type]:
        if not data["header"].get(field, False):
            missing_fields.append(field)
    for field in required_line_fields[move_type]:
        for line in data["lines"]:
            if not line.get(field, False):
                missing_fields.append(field)

    return missing_fields if missing_fields else False


def auto_create_invoice(sale_order) -> list:
    """
    execute all necessary steps to create an invoice from sale order
    """
    # sale_order = request.env["sale.order"].with_user(1).browse(order_id)
    for line in sale_order.order_line:
        line.qty_delivered = line.product_uom_qty
    invoice_vals = sale_order._prepare_invoice()
    # _logger.warning(invoice_vals)
    invoice_ids = sale_order._create_invoices()
    return invoice_ids


def search_stock_picking(sale_order) -> list:
    """
    Confirm stock picking
    """
    pickings = sale_order.mapped("picking_ids")

    domain = [("id", "in", pickings.ids)]
    stock_picking_ids = request.env["stock.picking"].with_user(1).search(domain)

    for move in stock_picking_ids:
        _logger.info(move)
        for line in move.move_line_ids_without_package:
            _logger.info(line)
            line.write({"qty_done": line.product_uom_qty})
        move.button_validate()
    return stock_picking_ids

def create_sale_order(user_id: int, data: dict) -> dict:
    """
    returns dictionary:
        - sale_order_id: sale_order object or 0 if error,
        - status : (success or error)
        - message : ""
    """
    sale_data = data.get("header")
    if not sale_data:
        return {"sale_order_id": 0, "status": "error", "error": "No data found"}
    if not partner_exists(sale_data.get("partner_id", 0)):
        return {"sale_order_id": 0, "status": "error", "error": "Partner not found"}
    if not data.get("lines"):
        return {"sale_order_id": 0, "status": "error", "error": "No lines found"}
    sale_order_ids = []
    try:
        sale_obj = request.env["sale.order"].with_user(user_id)
        sorted_lines = _sort_lines(data["lines"])
        fuel_lines = sorted_lines[0]
        non_fuel_lines = sorted_lines[1]
        if fuel_lines:
            fuel_order = _create_sale_order(sale_data, sale_obj)
            fuel_order._add_lines(fuel_lines)
            sale_order_ids.append(fuel_order)
        if non_fuel_lines:
            non_fuel_order = _create_sale_order(sale_data, sale_obj)
            non_fuel_order._add_lines(non_fuel_lines)
            sale_order_ids.append(non_fuel_order)
    except Exception as e:
        _logger.error(e.args)
        return {"sale_order_id": 0, "status": "error", "message": e.args}
    return sale_obj.browse(order.id for order in sale_order_ids)


def _sort_lines(data:list) -> list:
    """
    return list of lists of dicts
    index 0 = lines where product_id is_fuel
    index 1 = lines where product_id not is_fuel
    """
    fuel_lines = []
    non_fuel_lines = []
    product_obj = request.env["product.product"].with_user(ADMIN_ID)
    for line in data:
        is_fuel = product_obj.browse(line["product_id"]).is_fuel
        if is_fuel:
            fuel_lines.append(line)
        else:
            non_fuel_lines.append(line)
    _logger.info(fuel_lines)
    return [fuel_lines,non_fuel_lines]

def _get_fuel_lines(data: list) -> list:
    fuel_lines = []
    product_obj = request.env["product.product"].with_user(ADMIN_ID)
    for line in data:
        is_fuel = product_obj.browse(line["product_id"]).is_fuel
        if is_fuel:
            fuel_lines.append(line)
    _logger.info(fuel_lines)
    return fuel_lines


def _get_non_fuel_lines(data: list) -> list:
    non_fuel_lines = []
    product_obj = request.env["product.product"].with_user(ADMIN_ID)
    for line in data:
        is_fuel = product_obj.browse(line["product_id"]).is_fuel
        if not is_fuel:
            non_fuel_lines.append(line)
    _logger.info(non_fuel_lines)
    return non_fuel_lines


def _create_sale_order(sale_data: dict, sale_obj: object) -> object:
    date_order = datetime.strptime(sale_data["date_order"], DEBO_DATE_FORMAT)
    sale_order = sale_obj.create(
        {
            "partner_id": sale_data.get("partner_id"),
            "date_order": date_order or datetime.now(),
            "state": "draft",
        }
    )
    sale_order.onchange_partner_id()
    sale_order.onchange_user_id()

    sale_order.write(
        {
            "partner_invoice_id": sale_data.get("partner_invoice_id")
            or sale_order.partner_invoice_id.id,
            "partner_shipping_id": sale_data.get("partner_shipping_id")
            or sale_order.partner_shipping_id.id,
            "pricelist_id": sale_data.get("pricelist_id") or sale_order.pricelist_id.id,
        }
    )
    return sale_order

    # sale_order.with_context(
    #     partner_id=sale_data.get("partner_id")
    # ).onchange_partner_id()
    # date_order = datetime.strptime(sale_data["date_order"], DEBO_DATE_FORMAT)
    # sale_order = sale_obj.create(
    #     {
    #         "partner_id": sale_data.get("partner_id"),
    #         "date_order": date_order or datetime.now(),
    #         "state": "draft",
    #     }
    # )
    # sale_order.onchange_partner_id()
    # sale_order.onchange_user_id()

    # sale_order.write({
    #     "partner_invoice_id": sale_data.get("partner_invoice_id") or sale_order.partner_invoice_id.id,
    #     "partner_shipping_id": sale_data.get("partner_shipping_id") or sale_order.partner_shipping_id.id,
    #     "pricelist_id": sale_data.get("pricelist_id") or sale_order.pricelist_id.id,
    # })
    # for line in data["lines"]:
    #     new_line = sale_line_obj.create(
    #         {
    #             "order_id": sale_order.id,
    #             "product_id": line["product_id"],
    #         }
    #     )
    #     new_line.product_id_change()
    #     new_line.write({
    #         "product_uom_qty": line.get("product_uom_qty") or new_line.product_uom_qty,
    #         "price_unit": line.get("price_unit") or new_line.price_unit,
    #         "pump_id" : line.get("pump_id"),
    #     })
    # return {
    #     "status": "Success",
    #     "message": "Sale order created successfully",
    #     "sale_order_id": sale_order,
    # }
