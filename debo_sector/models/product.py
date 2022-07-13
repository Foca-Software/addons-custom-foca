from odoo import models, fields, api, _


class ProductTemplate(models.Model):
    _inherit = "product.template"

    warehouse_ids = fields.Many2many(
        comodel_name="stock.warehouse",
        relation="prod_tmpl_stock_warehouse_rel",
        string="Warehouses"
    )


class ProductProduct(models.Model):
    _inherit = "product.product"

    sector_codes = fields.Char(compute="_compute_sector_codes")

    def _compute_sector_codes(self):
        for product in self:
            sectors = product.warehouse_ids.mapped("sector_id.code")
            product.sector_codes = ",".join(sectors)