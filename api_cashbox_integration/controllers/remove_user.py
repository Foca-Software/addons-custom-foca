# pylint: disable=protected-access
import logging

from odoo.http import request, route, Controller

_logger = logging.getLogger(__name__)

ADMIN_ID = 2


class RemoveUser(Controller):
    _name = "debo.cloud.connector.remove.user"

    @route(
        "/debocloud/remove_user",
        type="json",
        auth="none",
        methods=["POST"],
        csrf=False,
    )
    def remove_user(self, **kwargs):
        _logger.info("Removing User: %s", dict(**kwargs))
        spreadsheet = kwargs.get("spreadsheet", False)
        store_id = kwargs.get("store_id", False)
        user_id = kwargs.get("user_id", False)

        session_obj = request.env["cash.control.session"].with_user(ADMIN_ID)
        session_id = session_obj.get_session_by_id_debo(spreadsheet, store_id)
        user_removed = session_id._api_remove_user(user_id)
        if user_removed:
            return {
                "status": "success",
                "message": f"user removed from spreadsheet {session_id.id_debo}",
            }
        return {
            "status": "error",
            "message": "user could not be added to cashbox",
        }
