from odoo import models, fields, api


class FuelMoveLine(models.Model):
    _name = "fuel.move.line"
    _description = "Fuel Move Lines"
    # _order = "tank_id desc"

    session_id = fields.Many2one(comodel_name="cash.control.session", string="Session")
    id_debo = fields.Char(related="session_id.id_debo", string="Planilla")

    pump_id = fields.Many2one(comodel_name="stock.pump", string="Pump")
    pump_id_debo = fields.Char(related="pump_id.id_debo", string="ID DEBO")
    pump_code = fields.Char(related="pump_id.code", string="Code")
    tank_id = fields.Many2one(comodel_name="stock.location", related="pump_id.tank_id")
    product_id = fields.Many2one(
        comodel_name="product.product",
        related="tank_id.product_id",
        string="Product",
    )
    price = fields.Float(string="Price")
    initial_qty = fields.Float(string="Initial Quantity")
    final_qty = fields.Float(string="Final Quantity")
    manual_qty = fields.Float(string="Manual Quantity")
    cubic_meters = fields.Float(string="Cubic Meters")
    amount = fields.Float(string="Amount")
