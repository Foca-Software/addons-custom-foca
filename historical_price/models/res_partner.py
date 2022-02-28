from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    invoice_price_method = fields.Selection(
        selection=[("historical", "Historical"), ("current", "Current Price")],
        string="Price Method",
        default="historical",
        help = "Set if the price should be the on set on sale order or the current price"
    )
