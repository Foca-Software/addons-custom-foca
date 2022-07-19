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
        """Create account.move record that is paid in cash.
        invoice's debo_transaction_type = 'complement'.
        payment_method_id is not checked but referenced.
        'pay_now_journal_id' key is used for consistency between requests
        for invoices paid in cash but payment must be done separately
        to allow proper payment.cash_control_session_id assignation after session is closed

        Returns:
            dict: SUCCESS or ERROR + data
        """
        try:
            data = kwargs
            request.env.user = ADMIN_ID
            self.check_missing_fields(data)
            invoice_id = self.create_complement_invoice(data)
            invoice_id.action_post()
            payment_id = self.pay_invoice(invoice_id, data)
            res = {
                "status": "SUCCESS",
                "invoice": invoice_id.name,
                "status": invoice_id.invoice_payment_state,
                "payment": payment_id.name,
            }
            return res

        except Exception as e:
            _logger.error(e)
            try:
                #invoice might not be created and thus error handling fails
                if invoice_id:
                    invoice_id.button_draft()
                    invoice_id.button_cancel()
                    invoice_id.delete_number()
                return {"status": "ERROR", "message": e.args[0]}
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
            "store_id"
            "spreadsheet",
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

    def _get_session_id(self, spreadsheet: str,store_id:int) -> models.Model:
        session_obj = request.env["cash.control.session"].with_user(ADMIN_ID)
        session_id = session_obj.get_session_by_id_debo(spreadsheet, store_id)
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
            _logger.info(invoice_id.name)
            lines = self._add_invoice_lines(invoice_id, data["lines"])
            # invoice_id.update({"pay_now_journal_id": data["pay_now_journal_id"]})
            return invoice_id
        except Exception as e:
            msg = f"{','.join([arg for arg in e.args])}"
            _logger.error(msg)
            raise ValidationError(msg)

    def pay_invoice(self, invoice_id: models.Model, data: dict) -> models.Model:
        """Creates payment_group and payment models.Models to pay invoice in cash

        Args:
            invoice_id (models.Model): account.move
            data (dict): full JSON request

        Returns:
            models.Model: account.payment.group
        """
        payment_data = {
            "journal_id": data["pay_now_journal_id"],
            "payment_method_id": request.env.ref(
                "account.account_payment_method_manual_in"
            ).id,
        }
        payment_context = self._get_payment_context(invoice_id)
        payment_group = self._create_payment_group(invoice_id, payment_context)
        payment = self._create_payments(
            payment_data, payment_group, invoice_id, payment_context
        )
        self._compute_and_post_payment(payment_group)
        return payment_group

    def _get_payment_context(self, invoice_id: models.Model) -> dict:
        """execute 'register payment' button to get context values

        Args:
            invoice_id (models.Model): account.move

        Returns:
            dict: context values for payment creation
        """
        wizard = invoice_id.with_context(
            active_ids=invoice_id.ids,
            active_model="account.move",
        ).action_account_invoice_payment_group()
        context = wizard["context"]
        return context

    def _create_payment_group(
        self, invoice_id: models.Model, context: dict
    ) -> models.Model:
        """Create Payment Group (draft,customer)

        Args:
            invoice_id (models.Model): account.move
            context (dict): payment_context

        Returns:
            models.Model: account.payment.group
        """
        acc_pay_group_obj = request.env["account.payment.group"].with_user(ADMIN_ID)
        apg_vals_list = {
            "partner_id": context["default_partner_id"],
            "to_pay_move_line_ids": context["to_pay_move_line_ids"],
            "company_id": context["default_company_id"],
            "state": "draft",
            "partner_type": "customer",
        }
        payment_group = acc_pay_group_obj.with_context(
            active_ids=invoice_id.ids, active_model="account.move"
        ).create(apg_vals_list)
        return payment_group

    def _create_payments(
        self,
        payment_data: dict,
        payment_group: models.Model,
        invoice_id: models.Model,
        context: dict,
    ) -> models.Model:
        """Create payment in cash related to invoice_id and part of payment_group

        Args:
            payment_data (dict): journal_id, payment_method_id
            payment_group (models.Model): account.payment.group
            invoice_id (models.Model): account.move
            context (dict): payment_context

        Returns:
            models.Model: account.payment
        """
        acc_payment_obj = request.env["account.payment"].with_user(ADMIN_ID)
        payment_vals = {
            # inmutable fields
            "partner_id": invoice_id.partner_id.id,
            "payment_type": "inbound",
            "partner_type": "customer",
            "payment_group_id": payment_group.id,
            "amount": acc_payment_obj._compute_payment_amount(
                invoice_id,
                invoice_id.currency_id,
                invoice_id.journal_id,
                invoice_id.invoice_date,
            ),
            "company_id": invoice_id.company_id,
            "cash_control_session_id": invoice_id.cash_control_session_id.id,
            # payment_data dependant fields
            "journal_id": payment_data["journal_id"],
            "payment_method_id": payment_data["payment_method_id"],
        }
        payment_context = {
            "active_ids": invoice_id.ids,
            "active_model": "account.move",
            "to_pay_move_line_ids": context["to_pay_move_line_ids"],
        }
        payment_context.update(context)
        acc_payment = acc_payment_obj.with_context(payment_context).create(payment_vals)
        return acc_payment

    def _compute_and_post_payment(self, payment_group: models.Model) -> bool:
        """Execute necessary methods to fill computed fields on both payment
        and payment group objects,posts both

        Args:
            payment_group (models.Model): account.payment.group

        Returns:
            bool: True
        """
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
        return True

    def _get_invoice_vals(self, data: dict) -> dict:
        """process JSON request and creates 'vals' for invoice creation

        Args:
            data (dict): JSON request

        Returns:
            dict: Proper values for invoice creation
        """
        partner_id = self._get_partner_id(data)
        company_id = self._get_company_id(data["company_id"])
        session_id = self._get_session_id(data["spreadsheet"],data['store_id'])
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
            "invoice_user_id": session_id.user_id,
            "ref": data.get("ref", ""),
            "name": data.get("name", "/"),
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

    def _get_partner_id(self, data: dict) -> int:
        """process JSON request to return a proper partner id

        Args:
            data (dict): JSON request

        Returns:
            int: partner id
        """
        return data.get("partner_id", False) or self._anon_consumer_id().id

    def _anon_consumer_id(self) -> models.Model:
        return request.env.ref("l10n_ar.par_cfa")

    def _get_company_id(self, company_id: int) -> models.Model:
        return request.env["res.company"].with_user(ADMIN_ID).browse(company_id)
