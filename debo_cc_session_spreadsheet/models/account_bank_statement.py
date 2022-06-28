from odoo import models, _
from odoo.exceptions import UserError
from odoo.tools.misc import formatLang

import logging

_logger = logging.getLogger(__name__)


class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    def _balance_check(self):
        """
        OVERWRITE METHOD
        We need to add a distinctive 'transaction_type' to be able to unreconcile and unlink
        the statement_line that is created upon closing the cash statement with difference
        """
        for stmt in self:
            if not stmt.currency_id.is_zero(stmt.difference):
                if stmt.journal_type == "cash":
                    if stmt.difference < 0.0:
                        account = stmt.journal_id.loss_account_id
                        name = _("Loss")
                    else:
                        # statement.difference > 0.0
                        account = stmt.journal_id.profit_account_id
                        name = _("Profit")
                    if not account:
                        raise UserError(
                            _(
                                "Please go on the %s journal and define a %s Account. This account will be used to record cash difference."
                            )
                            % (stmt.journal_id.name, name)
                        )

                    values = {
                        "statement_id": stmt.id,
                        "account_id": account.id,
                        "amount": stmt.difference,
                        "name": _("Cash difference observed during the counting (%s)")
                        % name,
                        # THIS----------------------------
                        "transaction_type": "difference",
                        # --------------------------------
                    }
                    self.env["account.bank.statement.line"].create(values)
                else:
                    balance_end_real = formatLang(
                        self.env, stmt.balance_end_real, currency_obj=stmt.currency_id
                    )
                    balance_end = formatLang(
                        self.env, stmt.balance_end, currency_obj=stmt.currency_id
                    )
                    raise UserError(
                        _(
                            "The ending balance is incorrect !\nThe expected balance (%s) is different from the computed one. (%s)"
                        )
                        % (balance_end_real, balance_end)
                    )
        return True

    def revert_difference_line(self):
        for statement in self:
            statement.button_reopen()
            lines = statement.mapped("line_ids")
            difference_line = lines.filtered(
                lambda x: x.transaction_type == "difference"
            )
            difference_line.button_cancel_reconciliation()
            difference_line.unlink()
            _logger.info(difference_line)
