from odoo.exceptions import AccessError
from odoo.http import request, route, Controller, Response

from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

class OpenSession(Controller):
    _name = "debo.cloud.connector.open.session"

    @route("/debocloud/open_session", type="json", auth="none", methods=["POST"], csrf=False)
    def receive_data(self, **kwargs):
        #check request ok
        sent_user_id = kwargs.get('user_id', False)
        if not sent_user_id:
            return {
                "status": "ERROR",
                "user_id": 0,
                "message": "Credentials not found in request",
            }
        user_id = request.env['res.users'].sudo().search([('id','=',sent_user_id)])
        request.env.user = user_id
        request.env.company = user_id.company_id
        data = kwargs.get("data",False)
        if not data:
            # Response.status = "400 Bad Request"
            return {"status": "ERROR", "message": "Data not found in request"}

        try:
            cash_box = request.env['cash.control.config'].with_user(user_id).browse(data.get('cash_id',[]))
        except Exception as e:
            # Response.status = "400 Bad Request"
            return {"status": "ERROR", "message": "Cash box not found"}

        #try open
        try:
            if cash_box.session_state_info == 'opened':
                # Response.status= "200 OK"
                return {"status": "OK", "message": "Cash box %s already opened" %(cash_box.name)}
            # Response.status= "200 OK"
            cash_box.api_open_cashbox(balance='start')
            cash_box.current_session_id.id_debo = data.get('id_debo',False)
            cash_box.current_session_id.change_received = data.get('amount',0)

            pump_ids = data.get('pump_ids',False)
            if pump_ids:
                cash_box.current_session_id.pump_ids = [(6,cash_box.current_session_id.id,pump_ids)]
                cash_box.current_session_id.create_fuel_move_lines()
            return {"status": "OK", "message": "Cash box %s opened" %(cash_box.name)} 
        except Exception as e:
            # Response.status = "400 Bad Request"
            request.env["cash.control.session"].with_user(user_id).search(
                [("config_id", "=", data.get("cash_id", [])), ("state", "!=", "closed")]
            ).write({"state": "closed", "active": False})
            return {"status": "ERROR", "message": e.args[0]}