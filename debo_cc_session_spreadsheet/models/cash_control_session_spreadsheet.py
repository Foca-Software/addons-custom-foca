import json

from odoo import fields, models, api, _


class CashControlSessionSpreadsheet(models.Model):
    _name = "cash.control.session.spreadsheet"
    _description = "Cash Control Session Spreadsheet"

    @api.depends("cash_control_session_id")
    def _compute_session_spreadsheet_name(self):
        for record in self:
            session = record.cash_control_session_id
            record.update({"name": _(f"{session.id_debo}")})

    name = fields.Char(compute="_compute_session_spreadsheet_name")

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )

    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("validated", "Validated"),
        ],
        default="draft",
        required=True,
    )

    company_currency_id = fields.Many2one(
        related="company_id.currency_id", readonly=True
    )

    # Cash Control Session related fields
    ##
    cash_control_session_id = fields.Many2one(
        "cash.control.session",
        string="Cash Control Session",
        required=True,
        ondelete="cascade",
    )

    session_date_start = fields.Datetime(
        related="cash_control_session_id.date_start",
        string="Session Date Start",
        readonly=True,
    )

    session_date_end = fields.Datetime(
        related="cash_control_session_id.date_end",
        string="Session Date End",
        readonly=True,
    )

    session_balance_start = fields.Monetary(
        related="cash_control_session_id.statement_balance_start",
        currency_field="company_currency_id",
        string="Session Balance Start",
        readonly=True,
    )

    session_balance_end = fields.Monetary(
        related="cash_control_session_id.statement_balance_end_real",
        currency_field="company_currency_id",
        string="Session Balance End",
        readonly=True,
    )

    # Spreadsheet values
    ## Cash
    cash_amount_start = fields.Monetary(
        currency_field="company_currency_id",
        string="Cash Amount Start",
    )

    cash_amount_sales = fields.Monetary(
        currency_field="company_currency_id",
        string="Cash Amount Sales",
    )

    cash_refund_amount = fields.Monetary(
        currency_field="company_currency_id",
        string="Refund Amount",
    )

    ## Summarized
    cash_amount_end = fields.Monetary(
        currency_field="company_currency_id",
        string="Cash Amount End",
        compute="_compute_cash_amount_end",
    )

    @api.depends("cash_amount_start", "cash_amount_sales", "cash_refund_amount")
    def _compute_cash_amount_end(self):
        for record in self:
            record.update(
                {
                    "cash_amount_end": record.cash_amount_start
                    + record.cash_amount_sales
                    - record.cash_amount_end
                }
            )

    ## Products List
    product_list_widget = fields.Char(help="To show the product sales list.")

    @api.model
    def get_session_product_sales_list(self, spreadsheet_id):
        session = (
            self.env["cash.control.session.spreadsheet"]
            .search([("id", "=", spreadsheet_id)])
            .mapped("cash_control_session_id")
        )

        if session:
            res = []
            lines = (
                session.mapped("payment_ids")
                .mapped("reconciled_invoice_ids")
                .mapped("invoice_line_ids")
                .filtered(lambda l: l.product_id.is_fuel == False)
            )

            for line in lines:
                res.append(
                    {
                        "invoice_id": line.move_id.id,
                        "invoice_line_id": line.id,
                        "invoice": line.move_id.name,
                        "product": line.product_id.name,
                        "quantity": line.quantity,
                        "price_unit": line.price_unit,
                        "price_total": line.price_total,
                    }
                )
            return json.dumps(res)

        return False
