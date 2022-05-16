import string

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
    DEBO_DATE_FORMAT,
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
    _name = "debocloud.create.sale"

    @route("/debocloud/create/sale", type="json", auth="none", methods=["POST"], csrf=False)
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
                return {
                    "status": "Error",
                    "message": "Missing fields: %s" % ",".join(missing_fields),
                }
            if self._is_anon_consumer(payload):
                try:
                    payload["header"]["partner_id"] = self._get_partner_id(payload)
                except Exception as e:
                    _logger.error(e)
                    return {
                    "status": "Error",
                    "message": f"Error creating eventual customer: {e}",
                    }
            res = {}
            try:
                sale_orders = create_sale_order(user_id, payload)
                res["status"] = "SUCCESS"
                res["sale_order_ids"] = sale_orders
            except Exception as e:
                _logger.error(e)
            return res
            if res["status"] == "error":
                # Response.status = "400 Bad Request"
                return res
            sale = res["sale_order_id"]
            res["sale_order_id"] = sale.id
            _logger.info(sale)

    def _get_default_payment_journal(self, company_id: int) -> int:
        return (
            request.env["account.journal"]
            .search([("type", "=", "cash"), ("company_id", "=", company_id)], limit=1)
            .id
        )

    def _inbound_check_codes(self):
        return ["received_third_check"]

    def _inbound_card_codes(self):
        return ['inbound_debit_card','inbound_credit_card']

    def _get_name_from_number(self,number):
            padding = 8
            if len(str(number)) > padding:
                padding = len(str(number))
            return ('%%0%sd' % padding % number)

    def _is_anon_consumer(self,data:dict) -> bool:
        """
        return True if "id_debo" is in header and not partner_id
        """
        header = data.get("header")
        if not header:
            raise Exception("No header found")
        id_debo = header.get("id_debo")
        partner_id = header.get("partner_id")
        return id_debo == 0 and not partner_id

    def _is_eventual_customer(self, data:dict)-> bool:
        return data.get("eventual_customer")

    def _anon_consumer_id(self) -> object:
        return request.env.ref("l10n_ar.par_cfa")

    def _get_partner_id(self, data:dict) -> int:
        """
        Returns new eventual customer partner id
        or
        Returns 'consumidor final anonimo' id
        """
        if self._is_eventual_customer(data):
            partner_obj = request.env['res.partner'].with_user(1)
            vals = self._eventual_customer_data(data["eventual_customer"], partner_obj)
            eventual_customer = partner_obj.create_eventual(vals)
            return eventual_customer.id
        return self._anon_consumer_id().id

    def _eventual_customer_data(self, data:dict, partner_obj:object) -> dict:
        afip_responsiblity = data.get("afip_responsiblity")
        responsiblity_id = partner_obj.eventual_afip_identification_type(afip_responsiblity)
        doc_type = data.get("document_type")
        doc_type_id = partner_obj.eventual_document_type(doc_type)
        eventual_partner_data = {
            "name": data.get("name"), #mandatory
            "l10n_ar_afip_responsibility_type_id" : responsiblity_id, #mandatory
            "l10n_latam_identification_type_id" : doc_type_id, #mandatory
            "vat": data.get("vat"), #mandatory
            "street": data.get("street"), #optional
            "street2": data.get("street2"), #optional
            "city": data.get("city"), #optional
            "zip": data.get("zip"), #optional
            "country_id": data.get("country_id"), #optional
            "state_id": data.get("state_id"), #optional
        }
        return eventual_partner_data

# trash
