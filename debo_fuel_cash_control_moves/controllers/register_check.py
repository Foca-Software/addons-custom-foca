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


demo_data = {
    "planilla": "10938",
    "orig_journal_id": 6,
    "dest_journal_id": 9,
    "amount": 15000,
    "checks": [
        {
            "number": "88811",
            "issue_date" : "27/05/2022",
            "partner_id" : 214
        }
    ]
}


class TransferCheck(Controller):
    _name = "debocloud.create.transfer.check"

    @route(
        "/debocloud/create/transfer_check",
        type="json",
        auth="none",
        methods=["POST"],
        csrf=False,
    )
    def receive_data(self, **kwargs):
        try:
            data = kwargs or demo_data()
            request.env.user = ADMIN_ID
            # self.check_missing_fields(data)
            transfer_id = self.transfer_to_bank(data)
            check_ids = self.add_checks_to_transfer(transfer_id, data["checks"])
            # invoice_id.post()
            res = {"status": "SUCCESS", "transfer": transfer_id.name}
            return res

        except Exception as e:
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
        vals = {
            "cash_control_session_id": session_id.id,
            "communication": data.get("lot_number"),
            "journal_id": orig_journal_id,
            "destination_journal_id": dest_journal_id,
            "amount": data["amount"],
            "payment_date": datetime.strptime(data["date"], DEBO_DATE_FORMAT) if data.get("date")
            else datetime.today().strftime("%Y-%m-%d"),
            "payment_type": "transfer",
            "payment_method_id": payment_method.id,
        }
        transfer = request.env["account.payment"].with_user(ADMIN_ID).create(vals)
        return transfer

    def add_checks_to_transfer(
        self, transfer_id: models.Model, data: list
    ) -> models.Model:
        for line in data:
            transfer_id.check_ids = [
                (
                    transfer_id.id,
                    0,
                    self._get_check_vals(transfer_id,line),
                )
            ]
        return transfer_id.check_ids

    def _required_check_fields(self):
        fixed_fields = {
            "type": "third_check",
            "state": "holding",
        }
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
        check_vals = {
            "type": "third_check",
            "state": "transfered",
            "name": self._get_name_from_number(line["number"]),
            "number": line["number"],
            "issue_date": datetime.strptime(line["issue_date"], DEBO_DATE_FORMAT),
            "amount": line["amount"],
            # "currency_id": request.env.company.currency_id.id,
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

