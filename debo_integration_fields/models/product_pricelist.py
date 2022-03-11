from odoo import models, fields, api, _


class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    id_debo = fields.Char(string="ID_DEBO")