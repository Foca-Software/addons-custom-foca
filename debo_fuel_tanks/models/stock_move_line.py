from odoo import models,fields,api,_

class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    session_id_debo = fields.Char(string="Planilla", related="move_id.session_id_debo",store=True)