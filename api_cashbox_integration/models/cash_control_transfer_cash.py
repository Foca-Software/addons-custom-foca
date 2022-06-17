from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class CashControlTransferCash(models.Model):
    _inherit = "cash.control.transfer.cash"

    is_last_session_transfer = fields.Boolean()

    def action_transfer(self, ref: str = False, session_id: models.Model = False):
        close_orig = False
        if session_id:
            orig_st = self.env["account.bank.statement"].search(
                [("journal_id", "=", self.orig_journal_id.id), ('cash_control_session_id','=',session_id.id)],
                limit=1,
                order="id desc",
            )
        else:
            orig_st = self.env["account.bank.statement"].search(
                [("journal_id", "=", self.orig_journal_id.id), ("state", "=", "open")],
                limit=1,
                order="id desc",
            )
        if len(orig_st) == 0:
            orig_st = (
                self.env["account.bank.statement"]
                .with_context({"journal_id": self.orig_journal_id.id})
                .create(
                    {
                        "user_id": self.env.user.id,
                    }
                )
            )

            close_orig = True

        out_values = {
            "date": fields.Date.today(),
            "statement_id": orig_st.id,
            "journal_id": self.orig_journal_id.id,
            "amount": -self.amount or 0.0,
            "account_id": self.orig_journal_id.default_credit_account_id.id,
            #'account_id': self.orig_journal_id.company_id.transfer_account_id.id,
            "ref": ref or "tc-%s" % (self.id),
            "name": self.name,
            "transaction_type": "TRANSFER_OUT",
            # "transaction_type_cc_select" : "TRANSFER_OUT"
        }

        statement_line = self.env["account.bank.statement.line"].create(out_values)
        # orig_st.write({'line_ids': [(0, False, out_values)]})

        if close_orig:
            orig_st.balance_end_real = orig_st.balance_end
            orig_st.button_confirm_bank()

        self.orig_statement_line_id = statement_line.id
        self.state = "transfer"

    def action_receipt(self, ref: str = False):
        dest_st = self.dest_cash_control_id.current_session_id.statement_id
        self.dest_cash_control_id.transfer_pendientes = False
        if len(dest_st) == 0:
            raise ValidationError("La caja de destino esta cerrada")

        in_values = {
            "date": fields.Date.today(),
            "statement_id": dest_st.id,
            "journal_id": dest_st.journal_id.id,
            "amount": self.amount or 0.0,
            "account_id": dest_st.journal_id.company_id.transfer_account_id.id,
            "ref": ref or "tc-%s" % (self.id),
            "name": self.name,
            "transaction_type": "TRANSFER_IN",
        }

        # dest_st.write({'line_ids': [(0, False, in_values)]})
        statement_line = self.env["account.bank.statement.line"].create(in_values)

        self.dest_statement_line_id = statement_line.id
        self.state = "receipt"
