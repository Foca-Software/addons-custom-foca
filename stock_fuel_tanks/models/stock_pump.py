from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class StockPump(models.Model):
    _name = "stock.pump"
    _description = "Stock Pump"

    name = fields.Char(string="Name")
    code = fields.Char(string="Code")
    description = fields.Char(string="Description")
    tank_id = fields.Many2one(comodel_name='stock.location', string='Tank', domain="[('is_fuel_tank','=',True)]")
    product_id = fields.Many2one(related="tank_id.product_id", string='Product')
    

    #this should be in another module but for simplicity it's here
    id_debo = fields.Char(string="ID debo")