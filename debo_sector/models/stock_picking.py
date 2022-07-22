from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = "stock.picking"

    from_sector_id = fields.Many2one(
        related="location_id.lot_stock_warehouse_id.sector_id",
        string="From Sector",
    )
    dest_sector_id = fields.Many2one(
        related="location_dest_id.lot_stock_warehouse_id.sector_id",
        string="Dest Sector",
    )

    
