from odoo import models,fields,api,_
import logging
import json
from ..utils import data_sender

data_sender = data_sender.DataSender()
_logger = logging.getLogger(__name__)

class ComplementInvoiceConfig(models.Model):
    _inherit = "complement.invoice.config"

    def _get_config_fields(self):
        config_fields = self.read(['id','day','cash_control_config_id','company_id','perceptions_apply'])
        for config in config_fields:
            config['ID_CLIENTE_DEBO'] = config['company_id']
            del config['company_id']
        return config_fields

    def _get_config_line_fields(self):
        config_lines = self.config_line_ids.read(['partner_id','product_id','percentage','partner_max_amount','partner_min_amount'])
        for line in config_lines:
            del line['id']
            line['partner_id'] = line['partner_id']
            line['product_id'] = line['product_id']

        return config_lines

    def _get_debo_fields(self):
        config_fields = self._get_config_fields()
        config_line_fields = self._get_config_line_fields()

        debo_fields = {
            'config' : config_fields,
            'lines' : config_line_fields,
        }
        return debo_fields

    def _get_base_endpoint(self):
        config_params = self.env["ir.config_parameter"].sudo()
        proper_config = config_params.get_param("debo_cloud_conector.debo_endpoint")
        if not proper_config:
            return config_params.get_param("web.base.url")
        return proper_config

    def _get_final_endpoint(self):
        return "/guardarFacturaFcc"
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