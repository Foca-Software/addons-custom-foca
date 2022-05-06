from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    pump_id = fields.Many2one(
        comodel_name="stock.pump",
        string="Pump",
        compute="_compute_pump_id",
    )

    is_fuel_order = fields.Boolean(
        string='Is Fuel Sale',
        compute="_compute_is_fuel_order",
    )


    @api.depends('order_line')
    def _compute_is_fuel_order(self):
        for order in self:
            order.is_fuel_order = False
            for line in order.order_line:
                if line.product_id.is_fuel:
                    order.is_fuel_order = True
                    break

    @api.depends("order_line")
    def _compute_pump_id(self):
        for order in self:
            order.pump_id = False
            if order.is_fuel_order:
                order.pump_id = order.order_line[0].pump_id

    @api.constrains("order_line")
    def _check_fuel_lines_max(self):
        for order in self:
            fuel_lines = [line for line in order.order_line if line.product_id.is_fuel]
            if len(fuel_lines) > 1:
                raise ValidationError(_("Only one fuel line is allowed"))
