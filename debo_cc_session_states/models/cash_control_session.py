from odoo import fields, models, api, _


class CashControlSession(models.Model):
    _inherit = "cash.control.session"

    state = fields.Selection(
        selection="_state_selection_options",
    )

    @api.model
    def _state_selection_options(self):
        return [
            ("draft", _("Draft")),
            ("opened", _("Opened")),
            ("closed", _("Closed Shift")),
            ("spreadsheet_control", _("Spreadsheet Control")),
            ("final_close", _("Final Close")),
        ]
