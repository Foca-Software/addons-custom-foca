from odoo import models,fields,api,_

class ResBank(models.Model):
    _inherit = "res.bank"

    id_debo = fields.Char(string="ID DEBO")