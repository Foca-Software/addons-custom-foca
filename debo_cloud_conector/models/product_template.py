from odoo import models,fields,api,_

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    id_debo = fields.Char(string="ID Debo")