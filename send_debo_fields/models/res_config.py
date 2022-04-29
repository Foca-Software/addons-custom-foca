from odoo import models, fields, api, _


class ResConfigSetting(models.TransientModel):
    _inherit = "res.config.settings"

    debo_base_url = fields.Char(
        string="Debo Endpoint",
        config_parameter="debo_cloud_conector.debo_endpoint",
    )
