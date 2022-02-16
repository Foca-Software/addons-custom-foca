from odoo import models, fields, api

class ResCompany(models.Model):
    _inherit = 'res.company'

    debo_cloud_url = fields.Char(string="URL de Debo Cloud")