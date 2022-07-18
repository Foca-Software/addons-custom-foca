# account_check.view_account_payment_form_inherited
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


class RegisterCheck(Controller):
    _name = "debocloud.create.register.check"

    @route(
        "/debocloud/create/register_check",
        type="json",
        auth="none",
        methods=["POST"],
        csrf=False,
    )
    def receive_data(self, **kwargs):
        try:
            data = kwargs
            request.env.user = ADMIN_ID
            # self.check_missing_fields(data)
            transfer_id = self.register_check(data)
            check_ids = self.add_checks_to_transfer(transfer_id, data["checks"])
            _logger.info(check_ids.read())
            transfer_id.post()

            res = {"status": "SUCCESS", "transfer": transfer_id.read()}
            return res

        except Exception as e:
            _logger.error(e)
            return {"status": "ERROR", "message": e.args[0]}

    def _get_bank_payment_method(self, journal_id: int) -> models.Model:
        """get journal_id's manual outbound payment method

        Args:
            journal_id (int): destination journal_id

        Raises:
            ValidationError: origin journal has no manual payment method

        Returns:
            models.Model: account.payment.method
        """
        journal_obj = request.env["account.journal"].with_user(ADMIN_ID)
        bank_journal_id = journal_obj.browse(journal_id)
        payment_methods = bank_journal_id.outbound_payment_method_ids
        payment_method = payment_methods.filtered(
            lambda x: x.code == "delivered_third_check"
        )
        if not payment_method:
            raise ValidationError(
                _("To add checks journal must have a check payment method")
            )
        return request.env.ref(
            "account_check.account_payment_method_delivered_third_check"
        )

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

    def register_check(self, data: dict) -> models.Model:
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
        vals = {
            "cash_control_session_id": session_id.id,
            "debo_transaction_type" : "register_check",
            "journal_id": orig_journal_id,
            "destination_journal_id": dest_journal_id,
            "amount": data.get("amount", 0),
            "payment_date": datetime.strptime(data["date"], DEBO_DATE_FORMAT)
            if data.get("date")
            else datetime.today().strftime("%Y-%m-%d"),
            "payment_type": "transfer",
            "payment_method_id": payment_method.id,
        }
        transfer = request.env["account.payment"].with_user(ADMIN_ID).create(vals)
        return transfer

    def add_checks_to_transfer(
        self, transfer_id: models.Model, data: list
    ) -> models.Model:
        check_obj = request.env["account.check"].with_user(ADMIN_ID)
        for line in data:
            check = check_obj.create(self._get_check_vals(transfer_id, line))
            self._update_check(check, line, transfer_id)
            transfer_id.check_ids = [(4,check.id)]
            transfer_id.onchange_checks()
            transfer_id._compute_check()
            _logger.info(check.read())
        return transfer_id.check_id

    def _update_check(self, check, line, transfer_id):
        _logger.info("_update_check")
        partner_id = (
            request.env["res.partner"].with_user(ADMIN_ID).browse(line["partner_id"])
        )
        check._add_operation("holding", transfer_id, date=transfer_id.payment_date)
        check.write(
            {
                "partner_id": partner_id.id,
                "state": "holding",
                "owner_vat": partner_id.vat,
                "owner_name": partner_id.name,
                "bank_id": line["bank_id"],
            }
        )
        return check

    def _required_check_fields(self):
        return [
            "name",
            "number",
            "issue_date",
            "amount",
            "currency_id",
            "journal_id",
            "partner_id",
        ]

    def _get_check_vals(self, transfer_id: models.Model, line: dict) -> dict:
        _logger.info("_get_check_vals")
        check_vals = {
            "type": "third_check",
            "state": "holding",
            "name": self._get_name_from_number(line["number"]),
            "number": line["number"],
            "issue_date": datetime.strptime(line["issue_date"], DEBO_DATE_FORMAT),
            "amount": line["amount"],
            "journal_id": transfer_id.journal_id.id,
            "partner_id": line["partner_id"],
        }
        return check_vals

    def _get_name_from_number(self, number):
        padding = 8
        if not number:
            return ""
        if len(str(number)) > padding:
            padding = len(str(number))
        return "%%0%sd" % padding % number
