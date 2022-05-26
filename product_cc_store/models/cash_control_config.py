from odoo import models, fields, api


class CashControlConfig(models.Model):
    _inherit = "cash.control.config"

    def name_get(self):
        return [
            (config.id, f"{config.name}({config.store_id.name if config.store_id else ''})")
            for config in self
        ]