from odoo import models,fields,api,_

class StockPicking(models.Model):
    _inherit="stock.picking"

    pump_id = fields.Many2one(comodel_name="stock.pump", string="pump")
    session_id = fields.Many2one(comodel_name="cash.control.session", string="Session", related='sale_id.cash_control_session_id')
    session_spreadsheet = fields.Char(related='session_id.id_debo', string="Spreadsheet")

    
