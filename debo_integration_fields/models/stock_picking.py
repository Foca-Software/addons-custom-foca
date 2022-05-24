from odoo import models, fields, api, _


class StockPicking(models.Model):
    _inherit = "stock.picking"

    is_other_oil_sale_move = fields.Boolean(string="Is other Oil Card move")

    oil_card_number = fields.Char(string="Oil Card Number")