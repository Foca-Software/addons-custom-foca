from odoo.exceptions import ValidationError
from odoo.http import request, route, Controller, Response
from odoo.models import Model
from odoo import _
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

ADMIN_ID = 2


class TransferCash(Controller):
    _name = "debo.cloud.connector.transfer.cash"

    @route(
        "/debocloud/transfer_cash",
        type="json",
        auth="none",
        methods=["POST"],
        csrf=False,
    )
    def transfer_cash(self, **kwargs):
        """
        This method is used to Transfer Cash from POS cashbox to accumulator cashbox_id (accumulator)
        uses default accumulator casbox_id
        """
        data = kwargs
        # check if any needed field is missing
        missing_fields = self._check_missing_fields(data)
        if missing_fields:
            msg = ", ".join(missing_fields)
            return self._return_error("missing fields", msg)

        # check if user_id exists
        user_id = self._get_user(data)
        if not user_id:
            return self._return_error("user_id")
        #'login'
        request.env.user = user_id
        request.env.company = user_id.company_id
        # check if cashbox_id exists
        cashbox_id = self._get_cashbox(data)
        if not cashbox_id:
            return self._return_error("cashbox_id")

        try:
            amount = data.get("amount", False)
            session_id = self._get_session_id(data.get("planilla"))
            if session_id.has_final_cash_transfer:
                raise ValidationError("Session already has final transfer")
            context = {}
            context.update(request.env.context)
            action_context = {
                "default_orig_journal_id": session_id.statement_id.journal_id,
                "default_dest_cash_control_id": cashbox_id.accumulator_cash_id.id,
                "default_amount": amount,
                "default_is_acum_cash_control": False,
            }
            context.update(action_context)
            transfer_wizard = (
                request.env["cash.control.transfer.wizard"]
                .with_user(user_id.id)
                .with_context(context)
                .create({})
            )
            transfer_number = data.get("transfer_number", False)
            transfer_ref = f"{cashbox_id.name}:{session_id.id_debo}-{transfer_number}"
            transfer_movement = transfer_wizard.api_transfer_cash(
                ref=transfer_ref, session_id=session_id
            )
            is_last_transfer = data.get("is_last_session_transfer", False)
            if is_last_transfer:
                session_id.update({"has_final_cash_transfer" : True})
            return {
                "status": "SUCCESS",
                "message": "Transferencia realizada con éxito",
            }
        except Exception as e:
            _logger.error(e)
            return self._return_error("other", e.args[0])

    # ----------------------------------------------------------------------------------------------------------------------
    def _get_user(self, data: dict) -> object:
        sent_user_id = data.get("user_id", False)
        user_id = request.env["res.users"].sudo().browse(sent_user_id)
        return user_id

    def _check_missing_fields(self, data: dict) -> object:
        missing_fields = []
        for field in self._required_fields():
            if not data.get(field, False):
                missing_fields.append(field)
        return missing_fields

    def _required_fields(self) -> list:
        return ["user_id", "cashbox_id", "amount", "transfer_number"]

    def _get_cashbox(self, data: dict) -> object:
        user = request.env.user
        cashbox_id = (
            request.env["cash.control.config"]
            .with_user(user.id)
            .browse(data.get("cashbox_id"))
        )
        return cashbox_id

    def _get_session_id(self, planilla: str) -> Model:
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

    def _return_error(self, error_type: str, info: str = False) -> dict:
        messages = {
            "missing fields": f"Missing fields: {info}",
            "user_id": "Invalid User ID",
            "cashbox_id": "Invalid Cashbox ID",
            "other": f"Error al realizar la transferencia: {info}",
        }
        _logger.error(messages[error_type])
        return {
            "status": "ERROR",
            "message": messages[error_type],
        }
