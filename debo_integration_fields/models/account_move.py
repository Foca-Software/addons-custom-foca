from odoo import models, fields, api, _


class AccountMove(models.Model):
    _inherit = "account.move"

    session_id_debo = fields.Char(
        string="Spreadsheet",
        related="cash_control_session_id.id_debo",
        store=True,
    )

    oil_card_number = fields.Char(
        string="Oil Card Number",
    )


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    session_id_debo = fields.Char(
        string="Spreadsheet",
        related="move_id.session_id_debo",
        store=True,
    )
