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
        # self._onchange_product_id()

    # @api.constrains("product_id")
    # def constraint_product_not_available(self):
    #     if (
    #         self.move_id.debo_transaction_type == "complement"
    #         and self.product_id not in self.move_id.config_type.ci_product_ids
    #     ):
    #         raise ValidationError(
    #             _(
    #                 "This cashbox cannot create complement invoice for %s"
    #                 % self.product_id.name
    #             )
    #         )

    # TODO:
    # add to invoice line column_invisible parent.debo_transaction_type != 'complement'

    # @api.constrains("line_ids")
    # def constraint_price_not_changeable(self):
    #     # this won't work unless product's lst_price is up to date with pump prices
    #     if (
    #         self.move_id.debo_transaction_type == "complement"
    #         and self.move_id.config_type.ci_amount != "manual"
    #         and self.price_unit != self.product_id.lst_price
    #     ):
    #         raise ValidationError(_("This cashbox cannot change product price"))
