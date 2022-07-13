from odoo import models, fields


class CashControlConfig(models.Model):
    _inherit = "cash.control.config"

    is_fuel_cashbox = fields.Boolean()
    is_shop_cashbox = fields.Boolean()

    # TODO: add base field in cash_control_extension
    location_id = fields.Many2one(
        comodel_name="stock.location",
        string="Location",
        domain=[("usage", "=", "internal"), ("is_fuel_tank", "=", False)],
        help="Default location to deduce stock for non fuel products"
    )
