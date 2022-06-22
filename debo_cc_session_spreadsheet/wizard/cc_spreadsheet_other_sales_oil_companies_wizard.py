from odoo import fields, models


class CashControlSpreadsheetOtherSalesOilCompaniesWizard(models.TransientModel):
    _name = "cc.spreadsheet.other.sales.oil.companies.wizard"
    _description = "Cash Control Spreadsheet Other Sales Oil Companies Wizard"

    def _default_other_sales_oil_companies_lines(self):
        session_id = (
            self.env["cash.control.session.spreadsheet"]
            .browse(self._context.get("active_ids"))
            .session_id
        )
        return self.env["stock.picking"].search(
            [
                ("cash_control_session_id", "=", session_id.id),
                ("is_other_oil_sale_move", "=", True),
            ]
        )

    session_other_sale_oil_companies_ids = fields.Many2many(
        "stock.picking",
        relation="cc_spreadsheet_other_sale_oil_companies_wizard_rel",
        string="Other Sales Oil Companies",
        required=True,
        ondelete="cascade",
        default=_default_other_sales_oil_companies_lines,
    )

    def confirm_other_sales_oil_companies(self):
        return True
