from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    session_id_debo = fields.Char(
        string="Spreadsheet",
        related="cash_control_session_id.id_debo",
        store=True,
    )
