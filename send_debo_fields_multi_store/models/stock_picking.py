from odoo import models, fields, api
from ..utils import data_sender
import logging

_logger = logging.getLogger(__name__)
data_sender = data_sender.DataSender()


class StockPicking(models.Model):
    _inherit = "stock.picking"

    picking_is_done = fields.Boolean(compute="_compute_picking_is_done")
    picking_info_sent = fields.Boolean()

    def _compute_picking_is_done(self):
        for picking in self:
            if picking.state == "done":
                picking.picking_is_done = True
                picking.send_debo_fields()
            else:
                picking.picking_is_done = False

    def _get_base_endpoint(self):
        config_params = self.env["ir.config_parameter"].sudo()
        proper_config = config_params.get_param("debo_cloud_conector.debo_endpoint")
        if not proper_config:
            return config_params.get_param("web.base.url")
        return proper_config

    def _get_final_endpoint(self):
        return "/actualizarStock"

    def _get_debo_fields(self):
        stock_quant_obj = self.env["stock.quant"]
        debo_fields = {}
        if self.location_id and self.location_id.usage == "internal":
            outgoing_lines = []
            for line in self.move_line_ids_without_package:
                domain = [
                    ("product_id", "=", line.product_id.id),
                    ("location_id", "=", self.location_id.id),
                ]
                stock_quants = stock_quant_obj.search(domain)
                line_dict = {
                    "sector": self.from_sector_id.code,
                    "store" : self.store_id.id,
                    "product_id": line.product_id.id,
                    "location_id": self.location_id.id,
                    "quantity": stock_quants.quantity,
                }
                outgoing_lines.append(line_dict)
            debo_fields['outgoing'] = outgoing_lines
        if self.location_dest_id and self.location_dest_id.usage == "internal":
            incoming_lines = []
            for line in self.move_line_ids_without_package:
                domain = [
                    ("product_id", "=", line.product_id.id),
                    ("location_id", "=", self.location_dest_id.id),
                ]
                stock_quants = stock_quant_obj.search(domain)
                line_dict = {
                    "sector": self.dest_sector_id.code,
                    "store" : self.store_id.id,
                    "product_id": line.product_id.id,
                    "location_id": self.location_dest_id.id,
                    "quantity": stock_quants.quantity,
                }
                incoming_lines.append(line_dict)
            debo_fields['incoming'] = incoming_lines
        return debo_fields

    def send_debo_fields(self):
        if not self.session_id_debo and not self.picking_info_sent:
            try:
                info_sent = data_sender.send_debo_fields(
                    data=self._get_debo_fields(),
                    endpoint=f"{self._get_base_endpoint()}{self._get_final_endpoint()}",
                )
                self.picking_info_sent = info_sent
            except Exception as e:
                _logger.error(e)
                self.picking_info_sent = False
                pass  # we cannot raise any exception on compute or server will crash
