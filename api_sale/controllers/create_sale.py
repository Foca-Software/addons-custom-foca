from odoo.http import request, route, Controller
import logging

from ..utils.create_methods import (
    check_required_fields,
    create_payments_from_invoices,
    create_sale_order,
    confirm_or_unreserve_orders,
    create_invoices_from_sale,
)

_logger = logging.getLogger(__name__)

DEBO_SALE_ORDER_CODE = 101
DEBO_INVOICE_CODE = 102
DEBO_TEST_CODE = 103


class ReceiveData(Controller):
    _name = "debocloud.create.sale"

    @route(
        "/debocloud/create/sale", type="json", auth="jwt_debo_pos", methods=["POST"], csrf=False
    )
    def receive_data(self, **kwargs):
        data = kwargs
        self._check_general_request_format(data)
        sent_user_id = data["user_id"]
        user_id = request.env["res.users"].sudo().search([("id", "=", sent_user_id)])
        request.env.user = user_id
        request.env.company = request.env["res.company"].browse(data["company_id"])
        payload = data["payload"]
        res = {"status": "SUCCESS"}

        
        self._check_sale_request_format(payload)
        try:
            if self._is_anon_consumer(payload):
                payload["header"]["partner_id"] = self._get_partner_id(payload)
        except Exception as e:
            _logger.error(e)
            return self._return_error("eventual")
        try:
            sale_orders = create_sale_order(user_id, payload)
            _logger.info(f"Sale Order {sale_orders.ids} created")
            res["sale_order_ids"] = sale_orders.ids
        except Exception as e:
            # TODO: cancel/archive failed orders
            _logger.error(e)
            return self._return_error("sale", e.args)
        try:
            sale_orders.action_confirm()
            picking_ids = confirm_or_unreserve_orders(sale_orders, user_id)
            _logger.info(f"Pickings {picking_ids.ids} confirmed or unreserved")
            res["picking_ids"] = picking_ids.ids
        except Exception as e:
            # TODO: cancel/archive failed pickings
            _logger.error(e)
            return self._return_error("picking", e.args)
        try:
            if not self._invoice_required(payload["header"]):
                return res
            invoice_data = payload["invoice_data"]
            invoice_data.update({"oil_card_number": payload["header"].get("oil_card_number")})
            invoice_id = create_invoices_from_sale(sale_orders, invoice_data)
            _logger.info(f"Invoice {invoice_id.id} created")
            res["invoice_id"] = invoice_id.id
        except Exception as e:
            # TODO: cancel/archive failed invoices
            _logger.error(e)
            return self._return_error("invoice", e.args)
        try:
            invoice_id.action_post()
            payment_data = payload.get("payment_data",False)
            payment = create_payments_from_invoices(invoice_id, payment_data, user_id)
            if payment:
                _logger.info(f"Payment {payment.ids} created")
                res["payment_id"] = payment.ids
            elif invoice_id.state == "paid":
                res["payment"] = "Invoice was paid in cash"
            else:
                res["payment"] = "Invoice not paid"
        except Exception as e:
            # TODO: cancel/archive failed payments
            _logger.error(e)
            return self._return_error("payment", e.args)
        return res

    # def _payment_required(self, invoice: object, payment_data: dict) -> bool:
    #     invoice_is_paid = invoice.invoice_payment_state == "paid"
    #     return payment_data or not invoice_is_paid

    def _return_error(self, reason: str = "other", info: str = "") -> dict:
        reasons = {
            "other": "other",
            "missing user": "Credentials not found in request",
            "missing payload": "Payload not found",
            "missing company": "Company not found, or not valid",
            "missing code": "Move type not found",
            "fields": "Missing fields",
            "eventual": "Error creating eventual customer",
            "header": "Header not found in request",
            "lines": "Lines not found in request",
            "sale": "Error creating sale orders",
            "picking": "Error creating picking",
            "invoice": "Error creating invoice",
            "payment": "Error creating payment",
        }
        error = {
            "status": "ERROR",
            "message": f"{reasons[reason]}.{info}",
        }
        return error

    def _invoice_required(self,header:dict) -> bool:
        return header.get("invoice")

    def _check_general_request_format(self, data: dict) -> bool:
        sent_user_id = data.get("user_id")
        if not sent_user_id:
            return self._return_error("missing user")
        payload = data.get("payload")
        if not payload:
            return self._return_error("missing payload")
        company_id = payload.get("company_id")
        if not company_id:
            return self._return_error("missing company")
        return True

    def _check_sale_request_format(self, data: dict) -> dict:
        if not data.get("header"):
            return self._return_error("header")
        if not data.get("lines"):
            return self._return_error("lines")

    def _is_anon_consumer(self, data: dict) -> bool:
        """
        return True if "id_debo" is in header and not partner_id
        """
        header = data.get("header")
        if not header:
            raise Exception("No header found")
        id_debo = header.get("id_debo")
        partner_id = header.get("partner_id")
        return id_debo == 0 and not partner_id

    def _is_eventual_customer(self, data: dict) -> bool:
        return data.get("eventual_customer")

    def _anon_consumer_id(self) -> object:
        return request.env.ref("l10n_ar.par_cfa")

    def _get_partner_id(self, data: dict) -> int:
        """
        Returns returning eventual customer partner id
        or
        Returns new eventual customer partner id
        or
        Returns 'consumidor final anonimo' id
        """
        if self._is_eventual_customer(data):
            eventual_data = data["eventual_customer"]
            partner_obj = request.env["res.partner"].with_user(2)
            returning_eventual = self._get_partner_by_vat(
                partner_obj, eventual_data["vat"]
            )
            if returning_eventual:
                return returning_eventual.id
            vals = self._eventual_customer_data(partner_obj, eventual_data)
            eventual_customer = partner_obj.create_eventual(vals)
            return eventual_customer.id
        return self._anon_consumer_id().id

    def _get_partner_by_vat(self, partner_obj, vat: str) -> int:
        partner_id = partner_obj.search([("vat", "=", vat)], limit=1)
        return partner_id

    def _eventual_customer_data(self, partner_obj: object, data: dict) -> dict:
        afip_responsiblity = data.get("afip_responsiblity")
        responsiblity_id = partner_obj.eventual_afip_identification_type(
            afip_responsiblity
        )
        doc_type = data.get("document_type")
        doc_type_id = partner_obj.eventual_document_type(doc_type)
        eventual_partner_data = {
            "name": data.get("name"),  # mandatory
            "l10n_ar_afip_responsibility_type_id": responsiblity_id,  # mandatory
            "l10n_latam_identification_type_id": doc_type_id,  # mandatory
            "vat": data.get("vat"),  # mandatory
            "street": data.get("street"),  # optional
            "street2": data.get("street2"),  # optional
            "city": data.get("city"),  # optional
            "zip": data.get("zip"),  # optional
            "country_id": data.get("country_id"),  # optional
            "state_id": data.get("state_id"),  # optional
        }
        return eventual_partner_data
