from odoo import models, fields


class StockLocation(models.Model):
    _inherit = "stock.location"

    lot_stock_warehouse_id = fields.One2many(
        comodel_name="stock.warehouse",
        inverse_name="lot_stock_id",
        string="Stock Location for Warehouse",
    )
