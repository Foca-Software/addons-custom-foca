from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class StockPump(models.Model):
    _name = "stock.pump"
    _description = "Stock Pump"

    name = fields.Char()
    code = fields.Char()
    description = fields.Char()
    tank_id = fields.Many2one(
        comodel_name="stock.location",
        string="Tank",
        domain="[('is_fuel_tank','=',True)]",
    )
    product_id = fields.Many2one(related="tank_id.product_id", string="Product")
