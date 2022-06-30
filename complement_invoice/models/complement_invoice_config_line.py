from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ComplementInvoiceConfigLine(models.Model):
    _name = "complement.invoice.config.line"
    _description = "Complement Invoice Config Line"

    config_id = fields.Many2one(comodel_name="complement.invoice.config")

    partner_id = fields.Many2one(comodel_name="res.partner")
    percentage = fields.Float(digits=(5, 2))
    product_id = fields.Many2one(
        comodel_name="product.product",
        domain=[("is_fuel", "=", True)],
        string="Fuel Types",
        required=True,
    )

    partner_max_amount = fields.Float(string="Maximum Amount")
    partner_min_amount = fields.Float(string="Minimum Amount")
    config_id_day = fields.Selection(related="config_id.day", string="Day")

    @api.constrains("percentage")
    def _constraint_percentage(self):
        for line in self:
            if line.percentage == 0:
                raise ValidationError(_("Percentage cannot be 0"))

    @api.constrains("product_id")
    def _constraint_product_id(self):
        for line in self:
            if (
                line.product_id.id
                not in line.config_id.cash_control_config_id.type_id.ci_product_ids.ids
            ):
                raise ValidationError(
                    _(
                        "%s cannot be invoiced in %s"
                        % (
                            line.product_id.name,
                            line.config_id.cash_control_config_id.name,
                        )
                    )
                )

    @api.constrains("partner_max_amount", "partner_min_amount")
    def _constraint_max_min_amount(self):
        for line in self:
            if (
                line.partner_max_amount
                and line.partner_min_amount >= line.partner_max_amount
            ):
                raise ValidationError(
                    _("Minimum amount should always be less than Maximum amount")
                )
            if line.partner_min_amount < 0 or line.partner_max_amount < 0:
                raise ValidationError(
                    _("Minimum amount and Maximum amount should be possitive")
                )
