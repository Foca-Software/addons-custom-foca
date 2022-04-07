from odoo.exceptions import AccessError
from odoo.http import request, route, Controller, Response

from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


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
        cashbox_id = kwargs.get('cashbox_id',False)
        user_id = kwargs.get('user_id',False)
        if not cashbox_id or not user_id:
            return self._return_error("missing fields")
        cashbox = request.env['cash.control.config'].with_user(1).browse(cashbox_id)
        if not cashbox:
            return self._return_error("cashbox_id")
        if self._user_is_active(user_id):
            return self._return_error("active")
        user_added = cashbox.current_session_id._api_add_user(user_id)
        if user_added:
            return {
                'status': 'SUCCESS',
                'message': f'user added to cashbox {cashbox.name}',
            }
        else:
            return self._return_error("other")


    def _user_is_active(self, user_id):
        sessions_obj = request.env['cash.control.session'].with_user(1)
        open_sessions = sessions_obj.search([('state', '=', 'opened')])
        active_users = open_sessions.mapped('user_ids')
        _logger.info(open_sessions)
        _logger.info(active_users)
        if user_id in active_users.ids:
            return True
        else:
            return False

    def _return_error(self, error_type: str, info: str = False) -> dict:
        messages = {
            "missing fields": "Missing fields",
            "user_id": "Invalid User ID",
            "cashbox_id": "Invalid Cashbox ID",
            "active" : "User is already active in cashbox",
            "other": "No se pudo agregar el usuario",
        }
        _logger.error(messages[error_type])
        return {
            "status": "ERROR",
            "message": messages[error_type],
        }