from odoo import models,fields,api,_
import logging
import json
from ..utils import data_sender

data_sender = data_sender.DataSender()
_logger = logging.getLogger(__name__)

class ComplementInvoiceConfig(models.Model):
    _inherit = "complement.invoice.config"



    def action_test_read(self):
        _logger.info(json.dumps(self._get_debo_fields()))

    # send_debo_field = fields.Char(compute="_send_debo_fields")
    # def send_debo_fields(self):
    #     try:
    #         up_to_date = data_sender.send_debo_fields(
    #             data=self._get_debo_fields(),
    #             endpoint=f"{self._get_base_endpoint()}{self._get_final_endpoint()}",
    #         )
    #         if not up_to_date:
    #             _logger.warning(_("Error sending data to debo"))
    #     except Exception as e:
    #         _logger.error(e)
    #         raise Warning(e.args)

    def _get_base_endpoint(self):
        config_params = self.env["ir.config_parameter"].sudo()
        proper_config = config_params.get_param("debo_cloud_conector.debo_endpoint")
        if not proper_config:
            return config_params.get_param("web.base.url")
        return proper_config

    def _get_final_endpoint(self):
        return "/guardarConfiguracionComplemento"


    def _get_debo_fields(self):
        config_fields = self.read(['id','day','cash_control_config_id'])
        config_line_fields = self.config_line_ids.read(['partner_id','product_id','percentage','partner_max_amount','partner_min_amount'])
        summary_line_fields = self.summary_ids.read(['product_id','percentage'])
        debo_fields = {
            'config' : config_fields,
            'lines' : config_line_fields,
            'summary' : summary_line_fields
        }
        return debo_fields

    def write(self, vals_list):
        res = super().write(vals_list)
        if res:
            try:
                up_to_date = data_sender.send_debo_fields(
                    data=self._get_debo_fields(),
                    endpoint=f"{self._get_base_endpoint()}{self._get_final_endpoint()}",
                )
                if not up_to_date:
                    _logger.warning(_("Error sending data to debo"))
            except Exception as e:
                _logger.error(e)
                raise Warning(e.args)
        return res