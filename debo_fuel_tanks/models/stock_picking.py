from odoo import models,fields,api,_

class StockPicking(models.Model):
    _inherit = "stock.picking"

    session_id_debo = fields.Char(string="Planilla", related="cash_control_session_id.id_debo", store=True)