from odoo import models,fields

class FranchiseFranchise(models.Model):
    _name = 'franchise.franchise'
    _description = "Franchise"

    name = fields.Char()
    description = fields.Text()
    code = fields.Char()
    store_ids = fields.One2many(comodel_name='res.store', inverse_name='franchise_id', string="Stores")