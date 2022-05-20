from cgitb import reset
from odoo.http import request, route, Controller
import logging

from ..utils.pump_test import (
    create_sale_order,
    unreserve_orders,
    create_invoice_from_sale,
)

_logger = logging.getLogger(__name__)

class ReceiveData(Controller):
    _name = "debocloud.create.pump_test"

    @route(
        "/debocloud/create/pump_test",
        type="json",
        auth="none",
        methods=["POST"],
        csrf=False,
    )
    def receive_data(self, **kwargs):
        data = kwargs
        request.env.user = data.get("user_id")
        request.env.company = data.get("company_id")
        res = {"status": "SUCCESS"}
        try:
            order = create_sale_order(data.get("user_id"),data.get("line"))
            picking = unreserve_orders(order)
            invoice = create_invoice_from_sale(order)
            invoice.post()
            res["dispatch"] = invoice.name
        except Exception as e:
            _logger.error(e)
            return {"msg": e.args[0]}
        return res
