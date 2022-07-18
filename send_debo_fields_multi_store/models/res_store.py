from odoo import models, api
from ..utils import data_sender
import logging

_logger = logging.getLogger(__name__)
data_sender = data_sender.DataSender()

class ResStore(models.Model):
    _inherit = "res.store"

    def _get_base_endpoint(self):
        config_params = self.env["ir.config_parameter"].sudo()
        proper_config = config_params.get_param("debo_cloud_conector.debo_endpoint")
        if not proper_config:
            return config_params.get_param("web.base.url")
        return proper_config

    def _get_final_endpoint(self):
        return "/guardarSucursal"

    def _integration_needed_fields(self):
        return [
            "name",
            "id_debo",
        ]

    def _get_debo_fields(self):
        return self.read(self._integration_needed_fields())[0]

    @api.model
    def create(self, vals):
        res = super().create(vals)
        if res:
            try:
                data_sender.send_debo_fields(
                    data=res._get_debo_fields(),
                    endpoint=f"{self._get_base_endpoint()}{self._get_final_endpoint()}",
                )
            except Exception as e:
                _logger.error(e)
        return res

    def write(self, vals):
        res = super().write(vals)
        if res:
            try:
                data_sender.send_debo_fields(
                    data=self._get_debo_fields(),
                    endpoint=f"{self._get_base_endpoint()}{self._get_final_endpoint()}",
                )
            except Exception as e:
                _logger.error(e)
        return res
