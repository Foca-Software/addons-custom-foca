import json

from odoo import fields, models, api, _


def add_to_product_list(products: dict, name: str, line: models.Model) -> dict:
    """
    Add a product to the dict list of products.
    :param products: dict of products
    :param name: name of the product
    :param line: sale.order.line record
    :return: dict of products updated
    """
    invoice_status = line.order_id.invoice_status

    if products.get(name):
        if invoice_status == "to invoice":
            products[name]["product_qty_acc_check"] += line.product_uom_qty
            products[name]["product_total_acc_check"] += line.price_total
        if invoice_status == "invoiced":
            products[name]["product_qty"] += line.product_uom_qty
            products[name]["product_total"] += line.price_total
    else:
        if invoice_status == "to invoice":
            products[name] = {
                "product_qty_acc_check": line.product_uom_qty,
                "product_total_acc_check": line.price_total,
            }
        if invoice_status == "invoiced":
            products[name] = {
                "product_qty": line.product_uom_qty,
                "product_total": line.price_total,
            }

    return products


class CashControlSessionSpreadsheet(models.Model):
    _name = "cash.control.session.spreadsheet"
    _description = "Cash Control Session Spreadsheet"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    @api.depends("session_id")
    def _compute_session_spreadsheet_name(self):
        for record in self:
            session = record.session_id
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

    # Cash Control Session fields
    ##
    session_id = fields.Many2one(
        "cash.control.session",
        string="Cash Control Session",
        required=True,
        ondelete="cascade",
    )

    session_config_name = fields.Many2one(
        comodel_name="cash.control.config",
        related="session_id.config_id",
        string="Session Config",
        readonly=True,
    )

    session_date_start = fields.Datetime(
        related="session_id.date_start",
        string="Session Start",
        readonly=True,
    )

    session_date_end = fields.Datetime(
        related="session_id.date_end",
        string="Session End",
        readonly=True,
    )

    session_user_ids = fields.Many2many(
        related="session_id.user_ids",
        string="Session Users",
        readonly=True,
    )

    # Spreadsheet values
    ## Cash
    # TODO: Add a base automation task that updates
    # the session values when a spreadsheet value changes.
    cash_amount_start = fields.Monetary(
        currency_field="company_currency_id",
        tracking=True,
    )

    cash_amount_end = fields.Monetary(
        currency_field="company_currency_id",
        tracking=True,
    )

    cash = fields.Monetary(
        currency_field="company_currency_id",
        tracking=True,
    )

    ## Expenses
    expenses = fields.Monetary(
        currency_field="company_currency_id",
        tracking=True,
    )

    ## Cards
    cards_amount = fields.Monetary(
        currency_field="company_currency_id",
        compute="_compute_cards_amount",
        tracking=True,
    )

    @api.depends("session_id.payment_ids")
    def _compute_cards_amount(self):
        for record in self:
            record.update(
                {
                    "cards_amount": sum(
                        record.session_id.mapped("payment_ids")
                        .filtered(
                            lambda r: r.journal_id.inbound_payment_method_ids.code
                            in ["inbound_debit_card", "inbound_credit_card"]
                        )
                        .mapped("amount")
                    )
                }
            )

    ## Summary
    checking_account_invoices_amount = fields.Monetary(
        currency_field="company_currency_id",
        compute="_compute_checking_account_invoices_amount",
        tracking=True,
    )

    @api.depends("session_id.sale_order_ids")
    def _compute_checking_account_invoices_amount(self):
        for record in self:
            record.update(
                {
                    "checking_account_invoices_amount": sum(
                        record.session_id.mapped("sale_order_ids")
                        .filtered(lambda so: so.invoice_status == "to invoice")
                        .mapped("amount_total")
                    )
                }
            )

    checking_account_dispatches_amount = fields.Monetary(
        currency_field="company_currency_id",
        # compute="_compute_checking_account_dispatches_amount",
        tracking=True,
    )

    # TODO: _compute_checking_account_dispatches_amount when dispatches are implemented

    total_to_submit = fields.Monetary(
        currency_field="company_currency_id",
        compute="_compute_total_to_submit",
        tracking=True,
    )

    @api.depends("cash_amount_start", "expenses", "cards_amount")
    def _compute_total_to_submit(self):
        for record in self:
            # TODO: The real calculation should be:
            # Pumps Sales - Other Dispatches (?) + No Gas Products Sales + Perceptions (?) - (Checking Account Invoices + Checking Account Dispatches) + Prices Differences (?)
            # Values with "?" are not implemented yet and we need more info from the user.
            record.update(
                {
                    "total_to_submit": record.cash_amount_start
                    + record.expenses
                    + record.cards_amount
                }
            )

    submited_total = fields.Monetary(
        currency_field="company_currency_id",
        compute="_compute_submited_total",
        tracking=True,
    )

    @api.depends("cash_amount_end", "expenses", "cards_amount")
    def _compute_submited_total(self):
        for record in self:
            # TODO: The real calculation should be:
            # Cash + Credit Cards Sales + Expenses + Checks (?) + In Vouchers (?) + Advanced Payment (?) - Out Vouchers (?) + Cash Amount Start - Cash Amount End
            # Values with "?" are not implemented yet and we need more info from the user.
            record.update(
                {
                    "submited_total": record.cash_amount_end
                    + record.expenses
                    + record.cards_amount
                }
            )

    session_difference = fields.Monetary(
        currency_field="company_currency_id",
        compute="_compute_session_difference",
        tracking=True,
    )

    @api.depends("submited_total", "total_to_submit")
    def _compute_session_difference(self):
        for record in self:
            record.update(
                {"session_difference": record.submited_total - record.total_to_submit}
            )

    ## Products List
    product_list_widget = fields.Char(help="To show the product sales list.")

    @api.model
    def get_session_product_sales_list(self, spreadsheet_id):
        # TODO: This can be done better.
        # A text field with the json data should exist, to avoid the user to
        # query the db everytime the tables are loaded, just in create and
        # data change moments.
        session = (
            self.env["cash.control.session.spreadsheet"]
            .search([("id", "=", spreadsheet_id)])
            .mapped("session_id")
        )
        if session:
            res = {
                "products": {},
                "fuels": {},
            }
            products = res["products"]
            fuels = res["fuels"]
            lines = session.mapped("sale_order_ids").mapped("order_line")
            for line in lines:
                name = line.product_id.name
                if line.product_id.is_fuel:
                    fuels = add_to_product_list(fuels, name, line)
                else:
                    products = add_to_product_list(products, name, line)
            return json.dumps(res)
        return False
