import string
from odoo.addons.account.models.account_payment import account_payment

# from typing import Dict
from odoo.exceptions import AccessError
from odoo.http import request, route, Controller, Response

# from odoo import fields, http

from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

class OpenSession(Controller):
    _name = "debo.cloud.connector.open.session"

    @route("/debocloud/open_session", type="json", auth="none", methods=["POST"], csrf=False)
    def receive_data(self, **kwargs):
        #----------------------------------------------------------------------------------------------------------------------
        _logger.warning(kwargs)
        if "login" not in kwargs:
            return {
                "status": "ERROR",
                "user_id": 0,
                "message": "Credentials not found in request",
            }
        login = kwargs["login"]["username"]
        password = kwargs["login"]["password"]
        try:
            user_id = request.session.authenticate(
                request.session.db, login, password
            )  # TODO: use JWT instead
        except:
            # Response.status = "401 Unauthorized"
            return {"status": "ERROR", "message": "Wrong username or password"}
        #----------------------------------------------------------------------------------------------------------------------
        # my_user = request.env['res.users'].sudo().search([('id','=',2)])
        # request.env.user = my_user
        # request.env.company = my_user.company_id
        data = kwargs.get("data",False)
        if not data:
            # Response.status = "400 Bad Request"
            return {"status": "ERROR", "message": "Data not found in request"}

        try:
            cash_box = request.env['cash.control.config'].with_user(user_id).browse(data.get('cash_id',[]))
        except Exception as e:
            # Response.status = "400 Bad Request"
            return {"status": "ERROR", "message": "Cash box not found"}

        try:
            if cash_box.session_state_info == 'opened':
                # Response.status= "200 OK"
                return {"status": "OK", "message": "Cash box %s already opened" %(cash_box.name)}
            # Response.status= "200 OK"
            cash_box.api_open_cashbox(coin_value=data.get('amount',False),balance='start')
            cash_box.current_session_id.id_debo = data.get('id_debo',False)
            return {"status": "OK", "message": "Cash box %s opened" %(cash_box.name)} 
        except Exception as e:
            # Response.status = "400 Bad Request"
            request.env["cash.control.session"].with_user(user_id).search(
                [("config_id", "=", data.get("cash_id", [])), ("state", "!=", "closed")]
            ).write({"state": "closed", "active": False})
            return {"status": "ERROR", "message": e.args[0]}