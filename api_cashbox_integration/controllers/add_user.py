from requests import session
from odoo.exceptions import AccessError
from odoo.http import request, route, Controller, Response

from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


ADMIN_ID = 2


class AddUser(Controller):
    _name = "debo.cloud.connector.add.user"

    @route(
        "/debocloud/add_user",
        type="json",
        auth="none",
        methods=["POST"],
        csrf=False,
    )
    def add_user(self, **kwargs):
        planilla = kwargs.get("planilla", False)
        store_id = kwargs.get("store_id", False)
        user_id = kwargs.get("user_id", False)
        session_obj = request.env["cash.control.session"].with_user(ADMIN_ID)
        if session_obj._user_is_active(user_id):
            return self._return_error("active")
        session_id = session_obj.get_session_by_id_debo(planilla, store_id)
        user_added = session_id._api_add_user(user_id)
        if user_added:
            return {
                "status": "SUCCESS",
                "message": f"User added to spreadsheet {session_id.id_debo}",
            }
        else:
            return self._return_error("other")

    def _return_error(self, error_type: str, info: str = False) -> dict:
        messages = {
            "missing fields": "Missing fields",
            "user_id": "Invalid User ID",
            "cashbox_id": "Invalid Cashbox ID",
            "active": "User is already active in cashbox",
            "other": "No se pudo agregar el usuario",
        }
        _logger.error(messages[error_type])
        return {
            "status": "ERROR",
            "message": messages[error_type],
        }
