#This configurations exceed FCO-149 specifications
#Further communication with Foca is needed
from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    complement_invoice_config_ids = fields.Many2many(comodel_name="complement.invoice.config", string="Complement Invoice Configurations")
    complement_invoice_config_line_ids = fields.One2many(comodel_name="complement.invoice.config.line", inverse_name="partner_id")
    
    complement_invoice_ids = fields.One2many(
        comodel_name="account.move",
        inverse_name="partner_id",
        string="Complement Invoices",
        domain=[('debo_transaction_type','=','complement')]
    )
