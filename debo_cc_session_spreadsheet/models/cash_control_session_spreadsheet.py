import json

from odoo import fields, models, api

from ..utils.complement_invoices_tools import check_missing_complement_invoice

IN_CHECK = "account_check.account_payment_method_received_third_check"


def add_to_product_list(products: dict, name: str, line: models.Model) -> dict:
    """
    Add a product to the dict list of products.
    :param products: dict of products
    :param name: name of the product
    :param line: sale.order.line record
    :return: dict of products updated
    """
    payment_state = line.move_id.invoice_payment_state

    if products.get(name):
        if payment_state == "not_paid":
            if not products[name].get("product_qty_acc_check"):
                products[name]["product_qty_acc_check"] = line.quantity
                products[name]["product_total_acc_check"] = line.price_total
            else:
                products[name]["product_qty_acc_check"] += line.quantity
                products[name]["product_total_acc_check"] += line.price_total
        if payment_state == "paid":
            if not products[name].get("product_qty"):
                products[name]["product_qty"] = line.quantity
                products[name]["product_total"] = line.price_total
            else:
                products[name]["product_qty"] += line.quantity
                products[name]["product_total"] += line.price_total
    else:
        if payment_state == "not_paid":
            products[name] = {
                "product_qty_acc_check": line.quantity,
                "product_total_acc_check": line.price_total,
            }
        if payment_state == "paid":
            products[name] = {
                "product_qty": line.quantity,
                "product_total": line.price_total,
            }

    return products


def add_to_fuel_list(fuels: dict, name: str, line: models.Model) -> dict:
    """
    Add a product to the dict list of products.
    :param fuels: dict of fuels detailed
    :param name: name of the fuel
    :param line: fuel.move.line record
    :return: dict of fuels detailed updated
    """

    vals = {
        "price": line.price,
        "id_debo": line.pump_id_debo,
        "code": line.pump_code,
        "initial_qty": line.initial_qty,
        "final_qty": line.final_qty,
        "manual_qty": line.manual_qty,
        "cubic_meters": line.cubic_meters,
        "amount": line.amount,
    }

    if not fuels.get(name):
        fuels[name] = []

    fuels[name].append(vals)

    return fuels


class CashControlSessionSpreadsheet(models.Model):
    _name = "cash.control.session.spreadsheet"
    _description = "Cash Control Session Spreadsheet"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    @api.model
    def create(self, vals_list):
        """This is needed to update the Total Sales at the
        creation time of the Cash Control Session Spreadsheet."""
        res = super().create(vals_list)
        self.get_session_fuel_detailed_list(res.id)
        return res

    @api.depends("session_id")
    def _compute_session_spreadsheet_name(self):
        for record in self:
            session = record.session_id
            record.update({"name": f"{session.id_debo}"})

    name = fields.Char(compute=_compute_session_spreadsheet_name)

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

    def action_spreadsheet_validate(self):
        """
        Button action to validate the cash control session spreadsheet
        and close the cash control session.
        """
        self.ensure_one()
        self.update({"state": "validated"})
        self.session_id.update({"state": "final_close"})

    def action_spreadsheet_draft(self):
        """
        Button action to back the cash control session spreadsheet
        to 'draft' state and the cash control session to 'spreadsheet_control'.
        """
        self.ensure_one()
        self.update({"state": "draft"})
        self.session_id.update({"state": "spreadsheet_control"})

    #############################
    # Cash Control Session fields
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

    session_pump_ids = fields.Many2many(
        related="session_id.pump_ids",
        string="Session Pumps",
        readonly=True,
    )

    session_payment_journal_ids = fields.Many2many(
        related="session_id.payment_journal_ids",
        string="Session Payment Methods",
        readonly=True,
    )

    ####################
    # Spreadsheet values
    ## Cash
    cash_amount_start = fields.Monetary(
        currency_field="company_currency_id",
        tracking=True,
    )

    cash_amount_end = fields.Monetary(
        currency_field="company_currency_id",
        tracking=True,
    )

    @api.depends("session_id.transfer_ids")
    def _compute_cash(self):
        for record in self:
            record.update({"cash": sum(self.session_id.mapped("transfer_ids.amount"))})

    cash = fields.Monetary(
        compute=_compute_cash,
        store=True,
        currency_field="company_currency_id",
        tracking=True,
    )

    ## Expenses
    expenses = fields.Monetary(
        currency_field="company_currency_id",
        tracking=True,
    )

    ## Checks
    @api.depends("session_id.payment_ids")
    def _compute_checks(self):
        for record in self:
            record.update(
                {
                    "checks_amount": sum(
                        self.session_id.mapped("payment_ids")
                        .filtered(
                            lambda p: p.journal_id.inbound_payment_method_ids
                            == self.env.ref(IN_CHECK)
                        )
                        .mapped("amount")
                    )
                }
            )

    checks_amount = fields.Monetary(
        compute=_compute_checks,
        store=True,
        currency_field="company_currency_id",
        tracking=True,
    )

    ## Cards
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

    cards_amount = fields.Monetary(
        currency_field="company_currency_id",
        compute=_compute_cards_amount,
        tracking=True,
    )

    ##########################
    # Complement Invoice Check

    @api.depends("session_id.complement_invoice_ids")
    def _compute_complement_invoice_check(self):
        for record in self:
            check_missing_complement_invoice(record, self.env)
            if not record.session_id.complement_invoice_ids:
                record.update({"complement_invoice_check": False})
            else:
                record.update({"complement_invoice_check": True})

    complement_invoice_check = fields.Boolean(
        compute=_compute_complement_invoice_check,
        tracking=True,
    )

    @api.depends("complement_invoice_check")
    def _compute_complement_invoice_missing_amount(self):
        for record in self:
            if not record.complement_invoice_check:
                # If total_fuel_sales (product lts sold by pump and product) - total_other_dispatches (same product) - total_pump_test_amount (same product) - total invoiced sales (same product) - total credit notes (same product) > abs(0.009) -> show message
                record.update({"complement_invoice_missing_amount": 150})

    complement_invoice_missing_amount = fields.Monetary(
        currency_field="company_currency_id",
        compute=_compute_complement_invoice_missing_amount,
        tracking=True,
    )

    #########
    # Summary

    ## Checking Account (I) - Cta. Cte. (FT)
    # Invoices not paid
    @api.depends("session_id.invoice_ids")
    def _compute_checking_account_invoices_amount(self):
        for record in self:
            record.update(
                {
                    "checking_account_invoices_amount": sum(
                        record.session_id.mapped("invoice_ids")
                        .filtered(
                            lambda i: i.invoice_payment_state != "paid"
                            and i.type == "out_invoice"
                        )
                        .mapped("amount_total")
                    )
                }
            )

    checking_account_invoices_amount = fields.Monetary(
        currency_field="company_currency_id",
        compute=_compute_checking_account_invoices_amount,
        tracking=True,
    )

    ## Checking Account (D) - Cta. Cte. (RE)
    # Sales total amount without invoice (sale orders)
    @api.depends("session_id.sale_order_ids")
    def _compute_sale_orders_not_invoiced_amount(self):
        for record in self:
            record.update(
                {
                    "sale_orders_not_invoiced_amount": sum(
                        record.session_id.mapped("sale_order_ids")
                        .filtered(lambda so: so.invoice_status == "to invoice")
                        .mapped("amount_total")
                    )
                }
            )

    sale_orders_not_invoiced_amount = fields.Monetary(
        currency_field="company_currency_id",
        compute=_compute_sale_orders_not_invoiced_amount,
        tracking=True,
    )

    #################
    # Total submitted
    @api.depends(
        "cash", "checks_amount", "cards_amount", "cash_amount_start", "cash_amount_end"
    )
    def _compute_submited_total(self):
        for record in self:
            record.update(
                {
                    "submited_total": record.cash
                    + record.checks_amount
                    + record.cards_amount
                    - record.cash_amount_start
                    + record.cash_amount_end
                }
            )

    submited_total = fields.Monetary(
        currency_field="company_currency_id",
        compute=_compute_submited_total,
        tracking=True,
        help="Total Cash + Total Checks + Total Cards - Cash Amount Start + Cash Amount End",
    )

    #################
    # Total to submit
    total_fuel_sales = fields.Monetary(
        currency_field="company_currency_id",
        tracking=True,
    )

    @api.depends("session_id.other_dispatch_line_ids")
    def _compute_total_other_dispatches(self):
        for record in self:
            record.update(
                {
                    "total_other_dispatches": sum(
                        record.session_id.mapped("other_dispatch_line_ids.price_total")
                    )
                }
            )

    total_other_dispatches = fields.Monetary(
        currency_field="company_currency_id",
        compute=_compute_total_other_dispatches,
        store=True,
        tracking=True,
    )

    @api.depends("session_id.pump_test_line_ids")
    def _compute_total_pump_test_amount(self):
        for record in self:
            record.update(
                {
                    "total_pump_test_amount": sum(
                        record.session_id.mapped("pump_test_line_ids.price_total")
                    )
                }
            )

    total_pump_test_amount = fields.Monetary(
        currency_field="company_currency_id",
        compute=_compute_total_pump_test_amount,
        store=True,
        tracking=True,
    )

    @api.depends("session_id.invoice_ids")
    def _compute_total_sales_no_oil_products(self):
        for record in self:
            lines = (
                record.session_id.mapped("invoice_ids")
                .mapped("invoice_line_ids")
                .filtered(lambda line: line.product_id.is_fuel is False)
            )
            record.update(
                {"total_sales_no_oil_products": sum(lines.mapped("price_total"))}
            )

    total_sales_no_oil_products = fields.Monetary(
        currency_field="company_currency_id",
        compute=_compute_total_sales_no_oil_products,
        store=True,
        tracking=True,
    )

    @api.depends(
        "total_fuel_sales",
        "total_pump_test_amount",
        "total_other_dispatches",
        "total_sales_no_oil_products",
    )
    def _compute_total_sales(self):
        for record in self:
            record.update(
                {
                    "total_sales": (
                        sum(
                            [
                                record.total_fuel_sales,
                                record.total_sales_no_oil_products,
                            ]
                        )
                        - record.total_other_dispatches
                        - record.total_pump_test_amount
                    )
                }
            )

    total_sales = fields.Monetary(
        currency_field="company_currency_id",
        compute=_compute_total_sales,
        store=True,
        tracking=True,
        help="Total Fuel Sales + Total No-Fuel Sales - Total Other Dispatches - Total Pump Tests",
    )

    @api.depends("total_sales", "checking_account_invoices_amount")
    def _compute_total_to_submit(self):
        for record in self:
            record.update(
                {
                    "total_to_submit": record.total_sales
                    - record.checking_account_invoices_amount
                }
            )

    total_to_submit = fields.Monetary(
        currency_field="company_currency_id",
        compute=_compute_total_to_submit,
        store=True,
        tracking=True,
        help="Total Sales - Invoices not paid (Checking Account)",
    )

    #################
    # Difference
    @api.depends("submited_total", "total_to_submit")
    def _compute_session_difference(self):
        for record in self:
            record.update(
                {"session_difference": record.submited_total - record.total_to_submit}
            )

    session_difference = fields.Monetary(
        currency_field="company_currency_id",
        compute=_compute_session_difference,
        tracking=True,
    )

    ###############################
    # Products and Fuel sales lists

    ## Products List Widget
    product_list_widget = fields.Char(help="To show the product sales list.")

    @api.model
    def get_session_product_sales_list(self, spreadsheet_id):
        # TODO: This can be done better.
        # A text field with the json data should exist, to avoid the user to
        # query the db everytime the tables are loaded, just in create and
        # data change moments. Also this will be needed for reports.
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
            lines = session.mapped("invoice_ids").mapped("invoice_line_ids")
            for line in lines:
                name = line.product_id.name
                if line.product_id.is_fuel:
                    fuels = add_to_product_list(fuels, name, line)
                else:
                    products = add_to_product_list(products, name, line)
            return json.dumps(res)
        return False

    ## Fuel Detailed List Widget
    fuel_detailed_list_widget = fields.Char(help="To show the fuel detailed list.")

    @api.model
    def get_session_fuel_detailed_list(self, spreadsheet_id):
        # TODO: This can be done better.
        # A text field with the json data should exist, to avoid the user to
        # query the db everytime the tables are loaded, just in create and
        # data change moments. Also this will be needed for reports.
        spreadsheet = self.env["cash.control.session.spreadsheet"].browse(
            spreadsheet_id
        )
        session = spreadsheet.session_id
        total_fuel_sales = 0
        if session:
            res = {
                "fuels": {},
            }
            fuels = res["fuels"]
            lines = session.mapped("fuel_move_ids")
            for line in lines:
                name = line.product_id.name
                fuels = add_to_fuel_list(fuels, name, line)
                total_fuel_sales += line.amount
            spreadsheet.update({"total_fuel_sales": total_fuel_sales})
            return json.dumps(res)
        return False
