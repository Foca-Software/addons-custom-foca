from odoo import models,fields,api,_

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    default_price = fields.Float(string="Default Product Price")