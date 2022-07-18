from odoo.http import request, route, Controller
import logging

from ..utils.other_oil_card_sale import (
    check_request_format,
    check_lines_format,
    create_oil_card_move,
    confirm_stock_moves,
    
)

_logger = logging.getLogger(__name__)

class ReceiveData(Controller):
    _name = "debocloud.create.other.oil.card.sale"

    @route(
        "/debocloud/create/other_oil_card_sale",
        type="json",
        auth="none",
        methods=["POST"],
        csrf=False,
    )
    def receive_data(self, **kwargs):
        try:
            data = kwargs
            request.env.user = data.get("user_id")
            request.env.company = data.get("company_id")
            res = {"status": "SUCCESS"}
            check_request_format(data)
            check_lines_format(data["lines"])
            picking_id = create_oil_card_move(data)
            confirm_stock_moves(picking_id)
            res["picking_id"] = picking_id.name
        except Exception as e:
            _logger.error(e)
            return {"status": "ERROR", "message": e.args[0]}
        return res
