from odoo import fields, models, api, _


class DeboConfig(models.Model):
    _name = "debo.config"
    _description = "Debo Config"

    name = fields.Char(string="Name", required=True)
    url = fields.Char(string="URL", required=True)
    default = fields.Boolean(string="Default", default=False)


    @api.constrains
    def _check_default(self):
        if self.search([('default', '=', True)]):
            if self.default:
                raise ValueError(_("Only one default config allowed"))
