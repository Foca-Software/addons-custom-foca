import logging
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SectorSector(models.Model):
    _name = "sector.sector"
    _description = "Sector"
    _order = "code asc"

    active = fields.Boolean(default=True)

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    description = fields.Text()

    company_id = fields.Many2one(
        comodel_name="res.company", default=lambda self: self.env.company
    )
    warehouse_ids = fields.One2many(
        comodel_name="stock.warehouse", inverse_name="sector_id", string="Warehouses"
    )
    id_debo = fields.Char()

    stock_quant_ids = fields.Many2many(
        comodel_name="stock.quant", compute="_compute_stock_quant_ids"
    )

    def inform_sector_stock(self):
        # stock_lists = []
        # for sector in self:
        #     stock_list = sector._get_sector_stock_list()
        #     stock_lists.append({f"{sector.code}": stock_list})
        return [{f"{sector.code}": sector._get_sector_stock_list()} for sector in self]
        # return stock_lists

    def _get_sector_stock_list(self):
        stock_list = self.stock_quant_ids.read(["product_id", "quantity"])
        if not stock_list:
            return {}
        for item in stock_list:
            del item["id"]
        return stock_list

    def _compute_stock_quant_ids(self):
        stock_quant_obj = self.env["stock.quant"]
        for sector in self:
            if not sector.warehouse_ids:
                sector.stock_quant_ids = False
                continue
            for warehouse in sector.warehouse_ids:
                stock_location = warehouse.lot_stock_id
                sector.stock_quant_ids = stock_quant_obj.search(
                    [("location_id", "=", stock_location.id)]
                )

    @api.constrains("name")
    def _constraint_name(self):
        for sector in self:
            domain = [
                ("name", "=", sector.name),
                ("company_id", "=", sector.company_id.id),
            ]
            name_already_exists = self.search_count(domain) > 1
            if name_already_exists:
                raise ValidationError(_("Sector Name already exists"))

    @api.constrains("code")
    def _constraint_code(self):
        for sector in self:
            domain = [
                ("code", "=", sector.code),
                ("company_id", "=", sector.company_id.id),
            ]
            code_already_exists = self.search_count(domain) > 1
            if code_already_exists:
                raise ValidationError(_("Sector code already exists"))
