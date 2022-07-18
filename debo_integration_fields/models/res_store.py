from odoo import models, fields


class ResStore(models.Model):
    _inherit = "res.store"

    id_debo = fields.Char()
