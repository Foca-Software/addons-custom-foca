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
            return {
                'status': 'error',
                'message': 'cashbox_id or user_id is missing',
            }
        cashbox = request.env['cash.control.session'].browse(cashbox_id)
        if not cashbox:
            return {
                'status': 'error',
                'message': 'cashbox_id does not exist',
            }
        if cashbox._api_add_user(user_id)
            return {
                'status': 'success',
                'message': f'user added to cashbox {cashbox.name}',
            }
        else:
            return {
                'status': 'error',
                'message': 'user could not be added to cashbox',
            }