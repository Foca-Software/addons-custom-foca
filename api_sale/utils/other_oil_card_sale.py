from odoo import models
from odoo.http import request
from odoo.exceptions import ValidationError

import logging

_logger = logging.getLogger(__name__)
DEBO_DATE_FORMAT = "%d/%m/%Y"
ADMIN_ID = 2


def check_request_format(data: dict) -> bool:
    """Check if any necessary fields are missing from main request

    Args:
        data (dict): full JSON request

    Raises:
        ValidationError: if any fields in _needed_request_format are missing

    Returns:
        bool: True
    """
    if any(field not in data.keys() for field in _needed_picking_fields()):
        raise ValidationError("Fields missing in request")
    return True


def check_lines_format(data: dict) -> bool:
    """Check if any necessary fields are missing from lines

    Args:
        data (dict): key "lines" from JSON request

    Raises:
        ValidationError: if any fields in _needed_lines_fields() are missing in
        all lines

    Returns:
        bool: True
    """
    if any(
        field not in line.keys() for field in _needed_lines_fields() for line in data
    ):
        raise ValidationError("Fields missing in lines")
    return True


def confirm_stock_moves(picking_id: models.Model) -> bool:
    """Confirm stock moves

    Args:
        picking_id (models.Model): stock.picking object

    Returns:
        bool: True if no errors were encountered
    """
    picking_id.action_assign()
    picking_id.button_validate()
    wizard_obj = request.env["stock.immediate.transfer"].with_user(ADMIN_ID)
    wiz = wizard_obj.create({"pick_ids": [(4, picking_id.id)]})
    wiz.process()
    return True


def create_oil_card_move(data: dict) -> models.Model:
    """Create a stock.picking record with stock.moves assigned to it

    Args:
        data (dict): full JSON request

    Returns:
        models.Model: stock.picking record
    """
    picking_id = _create_stock_picking(
        source=data["src_location_id"],
        destination=data["dest_location_id"],
        company_id=data["company_id"],
        planilla=data["spreadsheet"],
        store_id=data["store_id"],
        oil_card_number=data["oil_card_number"],
        origin=data.get("origin", False),
        partner_id=data.get("partner_id", False),
    )
    move_lines = _create_move_lines(data["lines"], picking_id)
    return picking_id


def _create_stock_picking(
    source: int,
    destination: int,
    company_id: int,
    planilla: str,
    store_id: int,
    oil_card_number: str,
    origin: str = "",
    partner_id: int = False,
) -> models.Model:
    """Private method creates stock.picking recordset

    Args:
        source (int): stock.location id from which the product is taken
        destination (int): stock.location id to which the product is taken
        company_id (int): res.company id to which the move belongs to
        planilla (str): number of 'planilla'
        oil_card_number (str): number of oil card used in transaction
        origin (str, optional): move origin description. Defaults to "".
        partner_id (int, optional): res.partner id if needed. Defaults to False.

    Returns:
        models.Model: stock.picking
    """
    stock_picking = request.env["stock.picking"].with_user(ADMIN_ID)
    picking_type = request.env["stock.picking.type"].with_user(ADMIN_ID)
    picking_type_id = picking_type.search(
        [
            ("default_location_src_id", "=", source),
            ("code", "=", "outgoing"),
        ],
        limit=1,
    )
    stock_picking_vals = {
        "company_id": company_id,
        "origin": origin,
        "cash_control_session_id": get_session_id(planilla, store_id).id,
        "is_other_oil_sale_move": True,
        "picking_type_id": picking_type_id.id,
        "location_id": source,
        "location_dest_id": destination,
        "partner_id": partner_id,
        "oil_card_number": oil_card_number,
    }
    stock_picking_id = stock_picking.create(stock_picking_vals)
    return stock_picking_id


def get_session_id(spreadsheet: str, store_id: int):
    session_obj = request.env["cash.control.session"].with_user(ADMIN_ID)
    session_id = session_obj.get_session_by_id_debo(spreadsheet, store_id)
    return session_id


def _create_move_lines(data: list, picking: models.Model) -> models.Model:
    """Create move lines

    Args:
        data (list): "lines" key of the JSON request
        picking (models.Model): stock.picking record

    Returns:
        models.Model: stock.move recordset
    """
    picking_context = _get_picking_context(picking)
    stock_obj = request.env["stock.move"].with_user(ADMIN_ID)
    moves = []
    line_nbr = 1
    for line in data:
        name = f"{picking.name}-{line_nbr}"
        stock_move = stock_obj.with_context(picking_context).create(
            _stock_vals(line, name)
        )
        moves.append(stock_move.id)
        line_nbr += 1
    return stock_obj.browse(moves)


def _get_picking_context(picking_id) -> dict:
    picking_context = {
        "default_company_id": picking_id.company_id.id,
        "default_picking_id": picking_id.id,
        "default_picking_type_id": picking_id.picking_type_id.id,
        "default_location_id": picking_id.location_id.id,
        "default_location_dest_id": picking_id.location_dest_id.id,
    }
    return picking_context


def _stock_vals(line: dict, name: str) -> dict:
    """Creates a dictionary of values used for stock.move creation

    Args:
        line (dict): each line of the "lines" list in the request
        name (str): stock move name

    Returns:
        dict: name,product_id,product_uom and quantity_done
    """
    product_obj = request.env["product.product"].with_user(ADMIN_ID)
    product_id = product_obj.browse(line["product_id"])
    stock_vals = {
        "name": f"OOCS-{name}",
        "product_id": product_id.id,
        "product_uom": product_id.uom_id.id,
        "quantity_done": line["quantity_done"],
    }
    return stock_vals


def _needed_picking_fields() -> list:
    """fields needed in main JSON request for endpoint to work

    Returns:
        list: list of needed fields
    """
    return [
        "user_id",
        "company_id",
        "spreadsheet",
        "store_id",
        "oil_card_number",
        "src_location_id",
        "dest_location_id",
        "lines",
    ]


def _needed_lines_fields() -> list:
    """fields needed in each line of lines key for endpoint to work

    Returns:
        list: list of needed fields
    """
    return ["product_id", "quantity_done"]
