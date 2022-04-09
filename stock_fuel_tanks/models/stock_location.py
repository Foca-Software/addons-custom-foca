from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class StockLocation(models.Model):
    _inherit = "stock.location"

    usage = fields.Selection(selection_add=[("fuel_tank", "Internal - Fuel Tank")])

    capacity = fields.Float(string="Capacity")
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
        domain=[("is_fuel", "=", True)],
    )
    pump_ids = fields.One2many(comodel_name='stock.pump', inverse_name='tank_id', string='Pumps')
    
    