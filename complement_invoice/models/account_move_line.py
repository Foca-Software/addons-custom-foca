from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    complement_percentage = fields.Float(digits=(5, 2))

    complement_product_id = fields.Many2one(
        comodel_name="product.product",
        string="Complement Product",
        domain=[("is_fuel",'=',True)],
    )

    @api.onchange('complement_product_id')
    def _onchange_complement_product_id(self):
        self.product_id = self.complement_product_id.id