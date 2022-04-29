from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = "res.company"
    
    id_debo = fields.Char(string="ID_DEBO")