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
        _logger.info("Received data:")
        _logger.info(kwargs)
        sent_user_id = kwargs.get('user_id', False)
        if not sent_user_id:
            return {
                "status": "ERROR",
                "user_id": 0,
                "message": "Credentials not found in request",
            }
        user_id = request.env['res.users'].sudo().search([('id','=',sent_user_id)])
        request.env.user = user_id
        _logger.info(user_id)
        _logger.info(request.env.user)
        # request.env.company = user_id.company_id
        payload = kwargs.get("payload", False)
        if not payload:
            return {"status": "Error", "message": "Payload not found"}

        company_id = payload.get("company_id", False)
        _logger.info(company_id)
        _logger.info(request.env.company)
        if not company_id:
            return {"status": "Error", "message": "Company not found, or not valid"}
        if company_id not in request.env.user.company_ids.ids:
            return {"status": "Error", "message": "User access denied to Company"}
        request.env.company = request.env["res.company"].browse(company_id)
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
                #TODO: CLEAN UP - method doesn't work
                #picking_ids = search_stock_picking(sale)
                
                #---------------------- STOCK PICKING HANDLING --------------------
                sale.action_confirm()
                picking_ids = request.env['stock.picking'].with_user(1).search([('sale_id','=',sale.id)])
                _logger.info(picking_ids)
                unreserve_required = any(line.product_id.is_fuel for line in sale.order_line)
                for picking in picking_ids:
                    if unreserve_required:
                        picking.do_unreserve()
                    else:
                        try:
                            picking.action_assign()
                            picking.button_validate()
                            wiz = request.env['stock.immediate.transfer'].with_user(user_id).create({'pick_ids': [(4, picking.id)]})
                            wiz.process()
                        except Exception as e:
                            _logger.error(e)
                            continue #TODO: handle this better
                            #this means that something failed while confirming the picking / stock move
                            #odoo response to this has not been specified      
                res["stock_picking_id"] = (
                    picking_ids[0].ids[0] if picking_ids else False
                )  # should always be only one
                #---------------------- STOCK PICKING HANDLING --------------------

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
                    # if it's not manual, will raise an error
                    if invoice.pay_now_journal_id:
                        payment_methods = (
                            invoice.pay_now_journal_id.inbound_payment_method_ids
                        )
                        payment_method = payment_methods.filtered(
                            lambda x: x.code == "manual"
                        )
                        if not payment_method:
                            invoice.pay_now_journal_id = False
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
            try:
                if created_invoices.invoice_payment_state == "paid":
                    return res
                payment_data = payload.get("payment_data", False)
                if not payment_data:
                    res["message"] = "Invoice is not Paid, Payment data not found"
                    return res
                # create payment and payment group objects
                acc_pay_group_obj = request.env["account.payment.group"].with_user(
                    user_id
                )
                acc_payment_obj = request.env["account.payment"].with_user(user_id)
                # --------------------------------------------------------------------------
                # execute 'register payment' button to get context values
                wizard = created_invoices.with_context(
                    active_ids=created_invoices.ids,
                    active_model="account.move",
                ).action_account_invoice_payment_group()
                context = wizard["context"]
                # --------------------------------------------------------------------------
                # create payment group
                to_pay_move_lines = context["to_pay_move_line_ids"]
                apg_vals_list = {
                    "partner_id": context["default_partner_id"],
                    "to_pay_move_line_ids": context["to_pay_move_line_ids"],
                    "company_id": context["default_company_id"],
                    "state": "draft",
                    "partner_type": "customer",
                }
                payment_group = acc_pay_group_obj.with_context(
                    active_ids=created_invoices.ids, active_model="account.move"
                ).create(apg_vals_list)
                # --------------------------------------------------------------------------
                # create payments
                if len(payment_data) > 1:
                    for payment_method in payment_data:
                        if "amount" not in payment_method.keys():
                            res["status"] = "Error"
                            res[
                                "message"
                            ] = "Payment data is not valid. If multiple payment methods are used, amount must be provided for each payment method"
                            return res
                for payment in payment_data:
                    payment_journal = request.env["account.journal"].with_user(user_id).browse(
                        payment["journal_id"]
                    )
                    payment_method = payment_journal.inbound_payment_method_ids
                    _logger.info(payment_method)
                    ap_vals_list = {
                        # inmutable fields
                        "partner_id": created_invoices.partner_id.id,
                        "payment_type": "inbound",
                        "partner_type": "customer",
                        "payment_group_id": payment_group.id,
                        "amount": payment.get("amount", False)
                        or acc_payment_obj._compute_payment_amount(
                            created_invoices,
                            created_invoices.currency_id,
                            created_invoices.journal_id,
                            created_invoices.invoice_date,
                        ),
                        # payment_data dependant fields
                        "journal_id": payment["journal_id"],
                        "payment_method_id": payment.get(
                            "payment_method_id", False
                        ),  # esto por ahi se puede computar
                        "company_id": context["default_company_id"],
                        # not required
                    }
                    payment_context = {
                        "active_ids": created_invoices.ids,
                        "active_model": "account.move",
                        "to_pay_move_line_ids": to_pay_move_lines,
                    }
                    payment_context.update(context)
                    acc_payment = acc_payment_obj.with_context(payment_context).create(
                        ap_vals_list
                    )
                    if acc_payment.journal_id.code in ['inbound_debit_card','inbound_credit_card']:
                        acc_payment.write({
                        "card_id": payment.get("card_id", False),  # computable?
                        "instalment_id": payment.get(
                            "instalment_id", False
                        ),  # computable?
                        "tiket_number": payment.get("ticket_number", False),
                        "card_number": payment.get("card_number", False),
                        "lot_number": payment.get("lot_number", False),
                        })

                # payment group compute methods
                payment_group._compute_payments_amount()
                payment_group._compute_matched_amounts()
                payment_group._compute_document_number()
                payment_group._compute_matched_amount_untaxed()
                payment_group._compute_move_lines()
                # payment compute methods
                for payment in payment_group.payment_ids:
                    payment._onchange_partner_id()
                    payment._compute_reconciled_invoice_ids()
                    payment.post()
                payment_group.post()
            except Exception as e:
                _logger.error(e)
                res["status"] = "Error"
                res["message"] = e.args

            return res

    def _get_default_payment_journal(self, company_id: int) -> int:
        return (
            request.env["account.journal"]
            .search([("type", "=", "cash"), ("company_id", "=", company_id)], limit=1)
            .id
        )


# trash
