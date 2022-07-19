from odoo import models, _
from odoo.http import request, route, Controller
from odoo.exceptions import ValidationError
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)
DEBO_DATE_FORMAT = "%d/%m/%Y"
ADMIN_ID = 2


class CardBatchLoad(Controller):
    _name = "debocloud.create.card.batch.load"

    @route(
        "/debocloud/create/card_batch_load",
        type="json",
        auth="none",
        methods=["POST"],
        csrf=False,
    )
    def receive_data(self, **kwargs):
        try:
            data = kwargs
            request.env.user = ADMIN_ID
            transfer = self.card_batch_load(data)
            transfer.post()
            res = {"status": "SUCCESS", "transfer": transfer.name}
            return res

        except Exception as e:
            _logger.error(e.args[0])
            return {"status": "ERROR"}

    def _needed_fields(self) -> list:
        return [
            "spreadsheet",
            "orig_journal_id",
            "dest_journal_id",
            "amount",
            "lot_number",
        ]

    def _get_session_id(self, spreadsheet: str,store_id:int) -> models.Model:
        session_obj = request.env["cash.control.session"].with_user(ADMIN_ID)
        session_id = session_obj.get_session_by_id_debo(spreadsheet, store_id)
        return session_id

    def card_batch_load(self, data: dict) -> models.Model:
        """Create transfer type payment from cash type journal to bank type journal

        Args:
            data (dict): request data

        Returns:
            models.Model: account.payment
        """
        dest_journal_id = data["dest_journal_id"]
        orig_journal_id = data["orig_journal_id"]
        payment_method = self._get_bank_payment_method(int(orig_journal_id))
        session_id = self._get_session_id(data["spreadsheet"],data['store_id'])
        # amount = self.compute_amount(session_id, dest_journal_id, data["amount"])
        amount = data["amount"]
        vals = {
            "cash_control_session_id": session_id.id,
            "debo_transaction_type" : "card_batch",
            "communication": data.get("lot_number"),
            "journal_id": orig_journal_id,
            "destination_journal_id": dest_journal_id,
            "amount": amount,
            "payment_date": datetime.strptime(data["date"], DEBO_DATE_FORMAT)
            if data.get("date")
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

    def _get_dest_journal_payment_summary(
        self, session_id: models.Model, dest_journal_id: int
    ) -> models.Model:
        payments = session_id.payment_summary_ids.filtered(
            lambda x: x.journal_id.id == dest_journal_id
        )
        return payments

    def compute_amount(
        self, session_id: models.Model, dest_journal_id: int, amount: float
    ) -> float:
        # Lot amounts should always be the TOTAL AMOUNT of payments received in 'dest_journal_id' regardless of
        # payments that were created correctly. Hence we should subtract the session's summary amount for that journal
        # from the sent amount.
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
        session_payment_summary = self._get_dest_journal_payment_summary(
            session_id, dest_journal_id
        )
        summary_amount = session_payment_summary.amount
        final_amount = amount - summary_amount
        if final_amount <= 0:
            raise ValidationError(
                "Sent amount is less than session's payments amount for destination journal"
            )
        else:
            return final_amount
