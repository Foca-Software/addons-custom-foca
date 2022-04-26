from odoo import models, fields, api, _


class AccountMove(models.Model):
    _inherit = "account.move"

    session_id_debo = fields.Char(
        string="Spreadsheet",
        related="cash_control_session_id.id_debo",
        store=True,
    )
