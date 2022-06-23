from xml.dom import ValidationErr
from odoo import api, fields, models,_
from odoo.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)

class ComplementInvoiceConfigLine(models.Model):
    _name = 'complement.invoice.config.line'
    _description = 'Complement Invoice Config Line'

    config_id = fields.Many2one(comodel_name="complement.invoice.config")
    
    partner_id = fields.Many2one(comodel_name='res.partner')
    percentage = fields.Float(digits=(5,2))
    product_ids = fields.Many2many(comodel_name='product.product', domain=[('is_fuel','=',True)], string="Fuel Types")

    partner_max_amount = fields.Float(related='partner_id.ci_maximum_amount')
    partner_min_amount = fields.Float(related='partner_id.ci_minimum_amount')
    config_id_day = fields.Selection(related="config_id.day",string="Day")

    @api.constrains('percentage')
    def _constraint_percentage(self):
        if self.percentage == 0:
            raise ValidationError(_("Percentage cannot be 0"))
        if self.percentage + self.config_id.total_percentage > 100:
            raise ValidationError(_("Total Configuration percentage cannot exceed 100"))

    @api.constrains('product_ids')
    def _constraint_product_ids(self):
        for product in self.product_ids:
            if product.id not in self.config_id.cash_control_config_id.type_id.ci_product_ids.ids:
                raise ValidationError(f"{product.name} cannot be invoiced in {self.config_id.cash_control_config_id.name}")


