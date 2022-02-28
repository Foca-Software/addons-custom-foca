from odoo import models, fields, api, _


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _prepare_invoice_line(self):
        res = super(SaleOrderLine, self)._prepare_invoice_line()
        if self.partner_id.invoice_price_method == "current":
            res["price_unit"] = self.product_id.lst_price
        return res

    partner_id = fields.Many2one(
        comodel_name="res.partner", string="Partner", related="order_id.partner_id"
    )
