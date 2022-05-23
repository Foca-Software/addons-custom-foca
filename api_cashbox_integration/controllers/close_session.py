from odoo.exceptions import AccessError
from odoo.http import request, route, Controller, Response

from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class CloseSession(Controller):
    _name = "debo.cloud.connector.close.session"

    @route(
        "/debocloud/close_session",
        type="json",
        auth="none",
        methods=["POST"],
        csrf=False,
    )
    def receive_data(self, **kwargs):
        sent_user_id = kwargs.get("user_id", False)
        if not sent_user_id:
            return self._return_error('user_id')
        user_id = request.env["res.users"].sudo().search([("id", "=", sent_user_id)])
        request.env.user = user_id
        request.env.company = user_id.company_id
        data = kwargs.get("data", False)
        if not data:
            return self._return_error('missing fields')

        try:
            cash_box = (
                request.env["cash.control.config"]
                .with_user(user_id)
                .browse(data.get("cash_id", []))
            )
        except Exception as e:
            return self._return_error('cashbox_id')

        try:
            """
            cash_control uses the same method to open and close a session, the only difference is
            the 'balance' argument (open/close). In this case we only create the closing statement
            """
            cash_box.api_open_cashbox(
                coin_value=data.get("amount", False), balance="close"
            )
            fuel_lines = data.get('fuel_moves', False)
            if fuel_lines:
                session_id = cash_box.current_session_id
                session_id._api_edit_fuel_lines(fuel_lines)
                session_id.create_stock_moves()
            cash_box.api_close_session()
            return {"status": "OK", "message": "Cash box %s Closed" % (cash_box.name)}
        except Exception as e:
            return self._return_error("other", info=e.args[0])

    def _return_error(self, error_type: str, info: str = False) -> dict:
        messages = {
            "missing fields": "Data not found in request",
            "user_id": "Invalid User ID",
            "cashbox_id": "Invalid Cashbox ID",
            "other": f"Cashbox could not be closed. {info or ''}",
        }
        _logger.error(messages[error_type])
        return {
            "status": "ERROR",
            "message": messages[error_type],
        }


