from odoo import models, fields, api, _


class ProductTemplate(models.Model):
    _inherit = "product.template"
    
    id_debo = fields.Char(string="ID_DEBO")
    
    store_id = fields.Many2one(comodel_name='res.users',default=lambda self: self.env.user.store_id)
