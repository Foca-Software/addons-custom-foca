from odoo import models,fields

class CashControlConfig(models.Model):
    _inherit="cash.control.config"

    sector_id = fields.Many2one(related='location_id.lot_stock_warehouse_id.sector_id')