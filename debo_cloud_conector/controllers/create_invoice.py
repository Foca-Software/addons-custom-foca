import string
from odoo.addons.account.models.account_payment import account_payment

# from typing import Dict
from odoo.exceptions import AccessError
from odoo.http import request, route, Controller, Response

# from odoo import fields, http

from datetime import datetime
import logging

from ..utils.create_methods import (
    auto_create_invoice,
    create_invoice,
    create_sale_order,
    check_required_fields,
    search_stock_picking,
)

_logger = logging.getLogger(__name__)

MOVE_TYPE_DICT = {
    "102": "out_invoice",
    "out_refund": "out_refund",
    "in_invoice": "in_invoice",
    "in_refund": "in_refund",
    "101": "sale_order",
}

DEBO_SALE_ORDER_CODE = 101
DEBO_INVOICE_CODE = 102
DEBO_TEST_CODE = 103


class ReceiveData(Controller):
    _name = "debo.cloud.connector.receive.data"

    @route("/debocloud/create", type="json", auth="none", methods=["POST"], csrf=False)
    def receive_data(self, **kwargs):
        _logger.warning(kwargs)
        # ---------------------------this won't be necessary once jwt is implemented----------------------------
        if "login" not in kwargs:
            return {
                "status": "ERROR",
                "user_id": 0,
                "message": "Credentials not found in request",
            }
        login = kwargs["login"]["username"]
        password = kwargs["login"]["password"]
        user_id = request.session.authenticate(
            request.session.db, login, password
        )  # TODO: use JWT instead
        if not user_id:
            return {"status": "Error", "message": "Wrong username or password"}
        # ------------------------------------------------------------------------------------------------------
        payload = kwargs.get("payload", False)
        if not payload:
            return {"status": "Error", "message": "Payload not found"}

        move_code = kwargs.get("move_type", False)
        if not move_code:
            return {"status": "Error", "message": "Move type not found"}

        if move_code == DEBO_SALE_ORDER_CODE:
            missing_fields = check_required_fields(payload, move_code)
            if missing_fields:
                return {
                    "status": "Error",
                    "message": "Missing fields: %s" % ",".join(missing_fields),
                }
            res = create_sale_order(user_id, payload)
            if res["status"] == "error":
                return res
            sale = res["sale_order_id"]
            res["sale_order_id"] = sale.id
            _logger.info(sale)
            sale.action_confirm()
            # stock related methods
            try:
                picking_ids = search_stock_picking(sale)
                _logger.info(picking_ids)
                res["stock_picking_id"] = (
                    picking_ids[0].ids[0] if picking_ids else False
                )  # should always be only one
            except Exception as e:
                _logger.error(e)
                res["status"] = "Error"
                res["message"] = "Error creating stock picking \n %s" % e.args
                return res
            # invoice related methods
            try:
                created_invoices = auto_create_invoice(sale)
                for invoice in created_invoices:
                    invoice.write(payload["invoice_data"])
                    invoice.action_post()
                _logger.info(created_invoices)
                res["invoice_ids"] = (
                    created_invoices[0].ids[0] if created_invoices else False
                )  # should always be only one
            except Exception as e:
                _logger.error(e)
                res["status"] = "Error"
                res["message"] = e.args
                return res

            return res

        if move_code == DEBO_INVOICE_CODE:
            missing_fields = check_required_fields(payload, move_code)
            if missing_fields:
                return {
                    "status": "Error",
                    "message": "Missing fields: %s" % ",".join(missing_fields),
                }
            return create_invoice(user_id, payload)

        if move_code == DEBO_TEST_CODE:
            res = request.env["account.move"].with_user(1).browse(333)
            acc_pay_group_obj = request.env["account.payment.group"].with_user(1)
            acc_payment_obj = request.env["account.payment"].with_user(1)
            # _logger.info(res)
            wizard = res.action_account_invoice_payment_group()
            context = wizard["context"]
            _logger.info(acc_payment_obj.default_get(context))
            # to_pay_move_lines = context['to_pay_move_line_ids']
            apg_vals_list = {
                "name": "yo le puse esto",
                "partner_id": context["default_partner_id"],
                "to_pay_move_line_ids": context["to_pay_move_line_ids"],
                "company_id": context["default_company_id"],
            }
            payment_group = acc_pay_group_obj.create(apg_vals_list)
            ap_vals_list = {
                "partner_id": payment_group.partner_id.id,
                "payment_type": "inbound",
                "partner_type": "customer",
                "payment_group_id": payment_group.id,
                "journal_id": res.journal_id.id,
                "payment_method_id": payload["payment_data"]["method_id"],
                "amount": acc_payment_obj._compute_payment_amount(
                    res, res.currency_id, res.journal_id, res.invoice_date
                ),
                "company_id": context["default_company_id"],
            }
            _logger.info(ap_vals_list)
            payment = acc_payment_obj.create(ap_vals_list)
            payment._onchange_partner_id()
            payment._onchange_journal()
            return {
                "res": res,
                "wizard": wizard,
                "payment_group": payment_group,
                "payment" : payment,
            }

        return {"status": "Error", "message": "Move type not found"}


# trash
