from odoo import models,fields,api,_
from ..utils import data_sender
import logging

_logger = logging.getLogger(__name__)

class AccountTax(models.Model):
    _inherit = "account.tax"

    product_ids = fields.Many2many(string="Productos", comodel_name='product.product', compute="_compute_product_ids")

    def _compute_product_ids(self):
        for record in self:
            record.product_ids = self.env["product.product"].search([("taxes_id", "in", record.id)])
    
    def write(self,vals):
        res = super().write(vals)
        for product in self.product_ids:
            try:
                if "amount" not in vals:
                    continue
                product.write({"write_date": fields.Datetime.now()})
            except Exception as e:
                _logger.error(e)
                raise Warning(e.args)
        return res
