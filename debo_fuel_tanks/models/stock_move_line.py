from odoo import models,fields,api,_

class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _default_session_id_debo(self):
        return self.move_id.cash_control_session_id.id_debo

    session_id_debo = fields.Char(string="Planilla", default=_default_session_id_debo)