from odoo import models,fields

class CashControlConfig(models.Model):
    _inherit="cash.control.config"

    sector_id = fields.Many2one(related='location_id.lot_stock_warehouse_id.sector_id')

    child_sector_ids = fields.Many2many(comodel_name='sector.sector',compute='_compute_sector_id')

    def _compute_sector_id(self):
        for config in self:
            child_locations = self.env['stock.location'].search([('location_id','=',config.sector_id)])
            config.child_sector_ids = [(6,0,[location.lot_stock_warehouse_id.sector_id for location in child_locations])]