from odoo import models, fields, api, _


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    pump_id = fields.Many2one(
        comodel_name="stock.pump", string="Pump",
        domain="[('product_id', '=', product_id)]",
    )

    # Esto deberia venir en el json de ventas
