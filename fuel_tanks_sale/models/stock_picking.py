from odoo import models, fields, api, _


class StockPicking(models.Model):
    _inherit = "stock.picking"

    pump_id = fields.Many2one(
        comodel_name="stock.pump",
        string="Pump",
        # compute="_compute_pump_id",
        related = "sale_id.pump_id",
        store=True,
    )

    is_fuel_picking = fields.Boolean("Is Fuel Picking", related="sale_id.is_fuel_order")

    @api.depends("sale_id")
    def _compute_pump_id(self):
        for picking in self:
            picking.pump_id = False
            if picking.sale_id:
                picking.pump_id = picking.sale_id.pump_id or False

    # TODO: if sale_id had many lines, only fuel lines should be unreserved
    # TODO: create a partial reception for non fuel lines
    # TODO: should that be optional, should it be in this module?
    # TODO: partial receptions for non fuel_line related pickings should not have a pump_id
