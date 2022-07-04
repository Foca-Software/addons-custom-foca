from odoo import models,fields

class ResStore(models.Model):
    _inherit = "res.store"

    franchise_id = fields.Many2one(comodel_name='franchise.franchise')
