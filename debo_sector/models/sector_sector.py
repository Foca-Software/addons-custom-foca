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
