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
        try:
            user_id = request.session.authenticate(
                request.session.db, login, password
            )  # TODO: use JWT instead
        except:
            # Response.status = "401 Unauthorized"
            return {"status": "Error", "message": "Wrong username or password"}
        # if not user_id:
        #     Response.status = "401 Unauthorized"
        # --------------------------------S----------------------------------------------------------------------
        _logger.warning(request.env.company)
        payload = kwargs.get("payload", False)
        if not payload:
            return {"status": "Error", "message": "Payload not found"}

        company_id = payload.get('company_id',False)
        if not company_id:
            return {"status": "Error", "message": "Company not found, or not valid"}
        if company_id not in request.env.user.company_ids.ids:
            return {"status": "Error", "message": "User access denied to Company"}
        request.env.company = request.env['res.company'].browse(company_id)
        move_code = kwargs.get("move_type", False)
        if not move_code:
            return {"status": "Error", "message": "Move type not found"}

        if move_code == DEBO_SALE_ORDER_CODE:
            missing_fields = check_required_fields(payload, move_code)
            if missing_fields:
                user_id = request.session.logout()
                return {
                    "status": "Error",
                    "message": "Missing fields: %s" % ",".join(missing_fields),
                }
            res = create_sale_order(user_id, payload)
            if res["status"] == "error":
                # Response.status = "400 Bad Request"
                return res
            sale = res["sale_order_id"]
            res["sale_order_id"] = sale.id
            _logger.info(sale)
            # stock related methods
            try:
                picking_ids = search_stock_picking(sale)
                _logger.info(picking_ids)
                res["stock_picking_id"] = (
                    picking_ids[0].ids[0] if picking_ids else False
                )  # should always be only one
                sale.action_confirm()
            except Exception as e:
                _logger.error(e)
                res["status"] = "Error"
                res["message"] = e.args
                # sale.button_cancel()
                # sale.unlink()
                return res
            # invoice related methods
            try:
                created_invoices = auto_create_invoice(sale)
                for invoice in created_invoices:
                    invoice.write(payload["invoice_data"])
                    # if not payload["invoice_data"].get("pay_now_journal_id", False):
                    #     invoice.pay_now_journal_id = self._get_default_payment_journal()
                    invoice.action_post()
                _logger.info(created_invoices)
                res["invoice_ids"] = (
                    created_invoices[0].ids[0] if created_invoices else False
                )  # should always be only one
            except Exception as e:
                _logger.error(e)
                res["status"] = "Error"
                res["message"] = e.args
                # picking_ids.unlink()
                # sale.unlink()
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
            invoice_id = payload["payment_data"]["invoice_id"]
            res = request.env["account.move"].with_user(user_id).browse(invoice_id)
            acc_pay_group_obj = request.env["account.payment.group"].with_user(user_id)
            acc_payment_obj = request.env["account.payment"].with_user(user_id)
            # _logger.info(res)
            wizard = res.with_context(
                active_ids=[res.id]
            ).action_account_invoice_payment_group()
            context = wizard["context"]
            # _logger.info(acc_payment_obj.default_get(context))
            # to_pay_move_lines = context['to_pay_move_line_ids']
            apg_vals_list = {
                "name": payload["payment_data"]["name"],
                "partner_id": context["default_partner_id"],
                "to_pay_move_line_ids": context["to_pay_move_line_ids"],
                "company_id": context["default_company_id"],
                "state": "draft",
                "partner_type": "customer",
            }
            payment_group = acc_pay_group_obj.with_context(active_ids=[res.id]).create(
                apg_vals_list
            )

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
            _logger.warn(request._context)
            payment = acc_payment_obj.with_context(active_ids=[res.id]).create(
                ap_vals_list
            )
            # payment_group compute methods
            payment._onchange_partner_id()
            payment._onchange_journal()
            payment._compute_reconciled_invoice_ids()
            payment_group.with_context(
                payment_group=res.id
            )._compute_matched_move_line_ids()
            payment_group._compute_matched_amounts()
            payment_group._compute_matched_amount_untaxed()
            payment_group._compute_move_lines()
            _logger.info("________PAYMENT GROUP________")
            _logger.info(payment_group.read())
            _logger.info("-----------PAYMENT------------")
            _logger.info(payment.read())
            return {
                "res": res,
                "wizard": wizard,
                "payment_group": payment_group,
                "payment": payment,
            }
            # payment._onchange_payment_method()

        return {"status": "Error", "message": "Move type not found"}

    def _get_default_payment_journal(self, company_id: int) -> int:
        return (
            request.env["account.journal"]
            .search([("type", "=", "cash"), ("company_id", "=", company_id)], limit=1)
            .id
        )


# trash
