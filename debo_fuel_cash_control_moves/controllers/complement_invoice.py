from odoo import models, _
from odoo.http import request, route, Controller
from odoo.exceptions import ValidationError
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)

# TODO: create new partner like other dispatch / pump_test?
# DEBO_TRANSFER_PARTNER = request.env.ref("debo_lot_crud?")
DEBO_DATE_FORMAT = "%d/%m/%Y"
ADMIN_ID = 2


def _demo_data():
    return {
        "planilla": "10938",
        "orig_journal_id": 6,
        "dest_journal_id": 16,
        "amount": 1500,
        "lot_number": 1100501,
    }


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
            data = kwargs or _demo_data()
            request.env.user = ADMIN_ID

            res = {"status": "SUCCESS", "invoice": "placeholder"}
            return res

        except Exception as e:
            _logger.error(f"F... {','.join([arg for arg in e.args])}")
            return {"status": "ERROR"}

    def _needed_fields(self) -> list:
        return [
            "planilla",
            "orig_journal_id",
            "dest_journal_id",
            "amount",
            "lot_number",
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

    def create_invoice(user_id: int, data: dict) -> dict:
        try:
            account_obj = request.env["account.move"].with_user(ADMIN_ID)
            move_line_obj = request.env["account.move.line"].with_user(ADMIN_ID)
            invoice_data = data["header"]
            invoice_id = account_obj.create(
                {
                    "partner_id": invoice_data["partner_id"],  # auto?
                    "partner_shipping_id": invoice_data[
                        "partner_shipping_id"
                    ],  # compute?
                    "ref": invoice_data.get("ref"),
                    "invoice_date": datetime.strptime(
                        invoice_data["invoice_date"], DEBO_DATE_FORMAT
                    ),
                    "journal_id": invoice_data.get("journal_id"),
                    # "l10n_latam_document_type_id": _get_doc_type_id(),
                    "company_id": invoice_data.get("company_id"),
                    # "currency_id": invoice_data["currency_id"], #compute
                    # not sent in the data
                    "type": "out_invoice",
                    "state": "draft",
                }
            )
            for line in data["invoice_line_ids"]:
                invoice_id.invoice_line_ids = [
                    (
                        0,
                        0,
                        {
                            "product_id": line["product_id"],
                            "name": line["name"],
                            "account_id": line["account_id"],
                            "quantity": line["quantity"],
                            "product_uom_id": line["product_uom_id"],
                            "price_unit": line["price_unit"],
                            "tax_ids": [(6, 0, [line["tax_ids"]])],
                            "exclude_from_invoice_tab": False,
                        },
                    )
                ]
        except ValueError as e:
            _logger.error(e.args)
            return {
                "invoice_id": invoice_id.id,
                "status": "error",
                "message": "Error creating invoice",
            }

        return {
            "invoice_id": invoice_id.id,
            "status": "success",
            "message": "Invoice created successfully",
        }

    def _get_line_value_ids(self, line: dict) -> dict:
        product_obj = request.env["product.product"].with_user(ADMIN_ID)
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

    def _create_invoice_lines(self, data: dict) -> models.Model:
        pass
