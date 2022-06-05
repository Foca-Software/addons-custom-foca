from odoo import fields, models


class CashControlSpreadsheetOtherDispatchesWizard(models.TransientModel):
    _name = "cc.spreadsheet.other.dispatches.wizard"
    _description = "Cash Control Spreadsheet Other Dispatches Wizard"

    def _default_other_dispatches_lines(self):
        return (
            self.env["cash.control.session.spreadsheet"]
            .browse(self._context.get("active_ids"))
            .session_id.other_dispatch_line_ids
        )

    session_other_dispatch_line_ids = fields.Many2many(
        "sale.order.line",
        relation="cc_spreadsheet_other_dispatch_line_wizard_rel",
        string="Other Dispatches",
        required=True,
        ondelete="cascade",
        default=_default_other_dispatches_lines,
    )

    def confirm_other_dispatches(self):
        return True
