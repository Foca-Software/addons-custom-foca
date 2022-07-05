from odoo import models,fields

class ResStore(models.Model):
    """All of this is to avoid adding fields to store form view which is annoying
    """
    _inherit = "res.store"

    is_ypf_franchise = fields.Boolean(compute="_compute_is_ypf_franchise")

    def _compute_is_ypf_franchise(self):
        for store in self:
            store.is_ypf_franchise = False
            if store.franchise_id == self.env.ref("debo_ypf_franchise.YPF_Franchise"):
                store.is_ypf_franchise = True