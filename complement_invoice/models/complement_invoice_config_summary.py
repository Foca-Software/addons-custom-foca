from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)

class ComplementInvoiceConfigSummary(models.Model):
    _name = 'complement.invoice.config.summary'
    _description = 'Complement Invoice Config Summary'

    config_id = fields.Many2one(comodel_name="complement.invoice.config")
    product_id = fields.Many2one(comodel_name="product.product")
    percentage = fields.Float(compute="_compute_percentage")

    def _compute_percentage(self):
        config_ids = self.mapped('config_id')
        for config in config_ids:
            amounts = config.config_line_ids.read_group(
                [('config_id','=',config.id)],
                ["percentage:sum"],
                ["product_id"],
            )
            vals = {}
            for amount in amounts:
                vals[amount['product_id'][0]] = amount['percentage']
            
            _logger.info(vals)
            for summary in self.filtered(lambda line: line.config_id.id == config.id):
                summary.percentage = vals.get(summary.product_id.id,0)
            # if vals:
            #     config.summary_ids = [(6,config.id,vals)]
            # else:
            #     config.summary_ids = False