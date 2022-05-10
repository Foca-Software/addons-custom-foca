from odoo import models,fields,api,_

class StockMove(models.Model):
    _inherit = "stock.move"

    def _default_session_id_debo(self):
        return self.cash_control_session_id.id_debo

    #TODO: make session_id_debo reliable on all models
    session_id_debo = fields.Char(string="Planilla", related="picking_id.session_id_debo")