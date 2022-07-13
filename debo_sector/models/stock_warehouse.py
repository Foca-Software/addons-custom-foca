from odoo import models, fields


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    sector_id = fields.Many2one(comodel_name="sector.sector", check_company=True)
