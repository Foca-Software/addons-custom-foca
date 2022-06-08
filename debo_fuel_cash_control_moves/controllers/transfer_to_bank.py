from odoo import models, _
from odoo.http import request, route, Controller
from odoo.exceptions import ValidationError
import logging
from datetime import datetime

# from ..utils.other_oil_card_sale import (
#     check_request_format,
#     check_lines_format,
#     create_oil_card_move,
#     confirm_stock_moves,
#     _get_cc_session_id
# )

_logger = logging.getLogger(__name__)

# TODO: create new partner like other dispatch / pump_test?
# DEBO_TRANSFER_PARTNER = request.env.ref("debo_lot_crud?")
DEBO_DATE_FORMAT = "%d/%m/%Y"
ADMIN_ID = 2


class TransferToBank(Controller):
    _name = "debocloud.create.transfer.to.bank"

    @route(
        "/debocloud/create/transfer_to_bank",
        type="json",
        auth="none",
        methods=["POST"],
        csrf=False,
    )
    def receive_data(self, **kwargs):
        try:
            data = kwargs
            request.env.user = ADMIN_ID
            # request.env.company = data.get("company_id")
            transfer = self.transfer_to_bank(data)
            transfer.post()
            res = {"status": "SUCCESS", "transfer": transfer.name}
            return res

        except Exception as e:
            _logger.error(e.args[0])
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
        session_id = session_obj.search([("id_debo", "=", planilla)],limit=1)
        if not session_id:
            raise ValidationError(_("Session not found"))
        return session_id

    def transfer_to_bank(self, data: dict) -> models.Model:
        """Create transfer type payment from cash type journal to bank type journal

        Args:
            data (dict): request data

        Returns:
            models.Model: account.payment
        """
        dest_journal_id = data['dest_journal_id']
        orig_journal_id = data['orig_journal_id']
        payment_method = self._get_bank_payment_method(int(orig_journal_id))
        session_id = self._get_session_id(data["planilla"])
        amount = self.compute_amount(session_id,dest_journal_id,data['amount'])
        vals = {
            "cash_control_session_id": session_id.id,
            "communication": data.get("lot_number"),
            "journal_id": orig_journal_id,
            "destination_journal_id": dest_journal_id,
            "amount": amount,
            "payment_date": datetime.strptime(data["date"], DEBO_DATE_FORMAT) if data.get("date")
            else datetime.today().strftime("%Y-%m-%d"),
            "payment_type": "transfer",
            "payment_method_id": payment_method.id,
        }
        transfer = request.env["account.payment"].with_user(ADMIN_ID).create(vals)
        return transfer

    def _get_bank_payment_method(self, journal_id: int) -> models.Model:
        """get journal_id's manual outbound payment method

        Args:
            journal_id (int): destination journal_id

        Raises:
            ValidationError: destination_journal_id has no manual payment method

        Returns:
            models.Model: account.payment.method
        """
        journal_obj = request.env["account.journal"].with_user(ADMIN_ID)
        bank_journal_id = journal_obj.browse(journal_id)
        payment_methods = bank_journal_id.outbound_payment_method_ids
        payment_method = payment_methods.filtered(lambda x: x.code == "manual")
        if not payment_method:
            raise ValidationError(_("Pay now journal must have manual method!"))
        return payment_method


    def _get_dest_journal_payment_summary(self,session_id: models.Model, dest_journal_id:int) -> models.Model:
        payments = session_id.payment_summary_ids.filtered(lambda x: x.journal_id.id == dest_journal_id)
        return payments

    def compute_amount(self,session_id:models.Model,dest_journal_id:int,amount:float) -> float:
        #Lot amounts should always be the TOTAL AMOUNT of payments received in 'dest_journal_id' regardless of
        #payments that were created correctly. Hence we should subtract the session's summary amount for that journal
        #from the sent amount.
        """Get final amount for transfer.

        Args:
            session_id (models.Model): cash.control.session
            dest_journal_id (int): journal_id to which cash is sent
            amount (float): TOTAL AMOUNT of payments that were suppossed to be imputed to dest_journal_id

        Raises:
            ValidationError: destination_journal_id has no manual payment method

        Returns:
            float: sent amount - payment_summary amount.
        """
        session_payment_summary = self._get_dest_journal_payment_summary(session_id,dest_journal_id)
        summary_amount = session_payment_summary.amount
        final_amount = amount - summary_amount
        if final_amount <= 0:
            raise ValidationError("Sent amount is less than session's payments amount for destination journal")
        else:
            return final_amount
