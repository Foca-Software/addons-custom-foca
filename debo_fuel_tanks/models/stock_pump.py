from odoo import models, fields, api, _

class StockPump(models.Model):
    _inherit = "stock.pump"

    id_debo = fields.Char(string="ID debo")