from odoo import models,fields,api,_

class StockMove(models.Model):
    _inherit = "stock.move"

    session_id_debo = fields.Char(string="Planilla", related="picking_id.session_id_debo", store=True)