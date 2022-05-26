from odoo import models,fields,api,_

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    default_price = fields.Float(string="Default Product Price")


    cash_control_session_id = fields.Many2one(string="Cash Control Session", related="order_id.cash_control_session_id")