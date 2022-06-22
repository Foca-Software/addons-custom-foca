from odoo import models, _
from odoo.http import request, route, Controller
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

DEBO_DATE_FORMAT = "%d/%m/%Y"
ADMIN_ID = 2


class ConfirmSession(Controller):
    _name = "debocloud.confirm.session"

    @route(
        "/debocloud/confirm_session",
        type="json",
        auth="none",
        methods=["POST"],
        csrf=False,
    )
    def receive_data(self, **kwargs):
        try:
            data = kwargs
            request.env.user = ADMIN_ID
            session_obj = request.env["cash.control.session"].with_user(ADMIN_ID)
            session_id = session_obj.get_session_by_id_debo(data.get("planilla"))
            session_id.confirm_session(data.get("change_delivered"))
            return {
                "session": session_id.name,
                "confirmed": session_id.is_confirmed_in_debo_pos,
                "change_delivered": session_id.change_delivered,
            }

        except Exception as e:
            return {"status": "ERROR", "message": e.args[0]}
