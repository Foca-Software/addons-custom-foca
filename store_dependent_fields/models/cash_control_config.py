from odoo import models,fields

class CashControlConfig(models.Model):
    _inherit = 'cash.control.config'

    location_ids = fields.Many2many(comodel_name="stock.location", string="Locations", domain=[('usage','=','internal')])
    # warehouse_id = fields.Many2one(comodel_name="stock.warehouse")