from odoo import models, fields, api


class ProductProduct(models.Model):
    _inherit = "product.product"

    cash_control_config_ids = fields.Many2many(
        comodel_name="cash.control.config", string="Cash boxes"
    )
