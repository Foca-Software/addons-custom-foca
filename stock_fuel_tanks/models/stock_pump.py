from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class StockPump(models.Model):
    _name = "stock.pump"
    _description = "Stock Pump"

    name = fields.Char(string="Name")
    code = fields.Char(string="Code")
    description = fields.Char(string="Description")
    tank_id = fields.Many2one(comodel_name='stock.location', string='Tank')
    product_id = fields.Many2one(related="tank_id.product_id", string='Product')
    