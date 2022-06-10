from odoo import models, _
from odoo.http import request, route, Controller
from odoo.exceptions import ValidationError
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)

DEBO_DATE_FORMAT = "%d/%m/%Y"
ADMIN_ID = 2


class ComplementInvoice(Controller):
    _name = "debocloud.create.complement.invoice"

    @route(
        "/debocloud/create/complement_invoice",
        type="json",
        auth="none",
        methods=["POST"],
        csrf=False,
    )
    def receive_data(self, **kwargs):
        try:
            data = kwargs
            request.env.user = ADMIN_ID
            self.check_missing_fields(data)
            invoice_id = self.create_complement_invoice(data)
            invoice_id.post()
            res = {"status": "SUCCESS", "invoice": invoice_id.name}
            return res

        except Exception as e:
            return {"status": "ERROR", "message": e.args[0]}

    def check_missing_fields(self, data: dict) -> bool:
        """Handles requests with not enough data

        Args:
            data (dict): JSON request

        Raises:
            ValidationError: Missing needed fields in request

        Returns:
            bool: True
        """
        missing_fields = any(
            field not in data.keys() for field in self._needed_fields()
        )
        missing_line_fields = any(
            field not in line.keys()
            for field in self._needed_line_fields()
            for line in data.get("lines", [])
        )
        if missing_fields or missing_line_fields:
            raise ValidationError("Missing needed fields in request")
        return True

    def _needed_fields(self) -> list:
        return [
            "company_id",
            "planilla",
            "journal_id",
            "pay_now_journal_id",
            "l10n_latam_document_type_id",
            "lines",
        ]

    def _needed_line_fields(self) -> list:
        return [
            "product_id",
            "quantity",
            "price_unit",
        ]

    def _get_session_id(self, planilla: str) -> models.Model:
        """gets cash_control_session object search by id_debo ('planilla')

        Args:
            planilla (str): id_debo, sent in request data

        Raises:
            ValidationError: no session_id was found

        Returns:
            models.Model: cash.control.session
        """
        session_obj = request.env["cash.control.session"].with_user(ADMIN_ID)
        session_id = session_obj.search([("id_debo", "=", planilla)], limit=1)
        if not session_id:
            raise ValidationError(_("Session not found"))
        return session_id

    def create_complement_invoice(self, data: dict) -> models.Model:
        """Create a client invoice with debo_transaction_type = 'complement'

        Args:
            data (dict): JSON request

        Raises:
            ValidationError: Non specific error while creation

        Returns:
            models.Model: account.move
        """
        try:
            account_obj = request.env["account.move"].with_user(ADMIN_ID)
            invoice_data = data
            invoice_id = account_obj.create(self._get_invoice_vals(invoice_data))
            lines = self._add_invoice_lines(invoice_id, data["lines"])
            return invoice_id
        except Exception as e:
            msg = f"{','.join([arg for arg in e.args])}"
            _logger.error(msg)
            raise ValidationError(msg)

    def _get_invoice_vals(self, data: dict) -> dict:
        """process JSON request and creates 'vals' for invoice creation

        Args:
            data (dict): JSON request

        Returns:
            dict: Proper values for invoice creation
        """
        partner_id = self._get_partner_id(data)
        company_id = self._get_company_id(data["company_id"])
        session_id = self._get_session_id(data["planilla"])
        invoice_date = (
            datetime.strptime(data["invoice_date"], DEBO_DATE_FORMAT)
            if data.get("invoice_date")
            else datetime.today().strftime("%Y-%m-%d")
        )
        invoice_vals = {
            "partner_id": partner_id,
            "partner_shipping_id": partner_id,
            "invoice_date": invoice_date,
            "journal_id": data["journal_id"],
            "l10n_latam_document_type_id": data["l10n_latam_document_type_id"],
            "company_id": company_id.id,
            "currency_id": company_id.currency_id.id,
            "cash_control_session_id": session_id.id,
            "pay_now_journal_id": data["pay_now_journal_id"],
            "invoice_user_id": session_id.user_id,
            "ref": data.get("ref", ""),
            "name" : data.get("name", "/"),
            # not sent in the data
            "type": "out_invoice",
            "debo_transaction_type": "complement",
            "state": "draft",
        }
        return invoice_vals

    def _get_line_vals(self, product_obj: models.Model, line: dict) -> dict:
        """process each line in JSON request 'lines' list

        Args:
            product_obj (models.Model): product.product
            line (dict): a value in lines list

        Returns:
            dict: proper vals to add as invoice_line_ids
        """
        product_id = product_obj.browse(line["product_id"])
        account_id = product_id.categ_id.property_account_income_categ_id
        return {
            "product_id": product_id.id,
            "name": product_id.name,
            "account_id": account_id.id,
            "quantity": line["quantity"],
            "product_uom_id": product_id.uom_id.id,
            "price_unit": line["price_unit"],
            "tax_ids": [(6, 0, product_id.taxes_id.ids)],
            "exclude_from_invoice_tab": False,
        }

    def _add_invoice_lines(self, invoice_id: models.Model, data: dict) -> models.Model:
        """Add lines to invoice

        Args:
            invoice_id (models.Model): account.move
            data (dict): JSON request

        Returns:
            models.Model: account.move
        """
        product_obj = request.env["product.product"].with_user(ADMIN_ID)
        for line in data:
            invoice_id.invoice_line_ids = [
                (
                    0,
                    0,
                    self._get_line_vals(product_obj, line),
                )
            ]
        return invoice_id.invoice_line_ids

    def _get_partner_id(self, data:dict) -> int:
        """process JSON request to return a proper partner id

        Args:
            data (dict): JSON request

        Returns:
            int: partner id
        """
        return data.get("partner_id", False) or self._anon_consumer_id().id

    def _anon_consumer_id(self) -> object:
        return request.env.ref("l10n_ar.par_cfa")

    def _get_company_id(self, company_id: int) -> models.Model:
        return request.env["res.company"].with_user(ADMIN_ID).browse(company_id)
