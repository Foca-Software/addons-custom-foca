import logging
from odoo import models,fields,api

class StockPicking(models.Model):
    _inherit='stock.picking'

    from_sector_id = fields.Many2one(related='location_id.lot_stock_warehouse_id.sector_id', string="From Sector")
    dest_sector_id = fields.Many2one(related='location_dest_id.lot_stock_warehouse_id.sector_id', string="Dest Sector")


    picking_is_done = fields.Boolean(compute='_compute_picking_is_done')
    picking_info_sent = fields.Boolean()

    def _compute_picking_is_done(self):
        for picking in self:
            if picking.state == 'done':
                picking.picking_is_done = True
                if not picking.session_id_debo and not picking.picking_info_sent:
                    logging.info("mira como te mando info mira")
                    logging.info(f"viene de {picking.from_sector_id.name}, sector: {picking.from_sector_id.name}")
                    logging.info(f"va a {picking.dest_sector_id.name}, sector: {picking.dest_sector_id.name}")
                picking.picking_info_sent = True
            else:
                picking.picking_is_done = False


    @api.onchange('picking_is_done')
    def _onchange_state_done(self):
        for picking in self:
            if picking.picking_is_done and not picking.session_id_debo:
                logging.info("mira como te mando info mira")
                logging.info(f"viene de {picking.from_sector_id.name}, sector: {picking.from_sector_id.name}")
                logging.info(f"va a {picking.dest_sector_id.name}, sector: {picking.dest_sector_id.name}")

