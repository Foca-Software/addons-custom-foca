from odoo import models, fields, api


class CashControlConfigType(models.Model):
    _inherit = "cash.control.config.type"

    uses_complement_invoice = fields.Boolean(store=True)
    ci_moment_of_creation = fields.Selection(
        [
            ("pos_closing", "Closing Pos Session"),
            ("pos_spreadsheet", "Pos Spreadsheet"),
            ("cloud_spreadsheet", "Cloud Spreadsheet"),
        ],
        string="Moment of Creation",
        help="Specifies when will Complement Invoices be created",
    )

    allow_cloud_ci_creation = fields.Boolean(compute="_compute_allow_ci_creation")

    def _compute_allow_ci_creation(self):
        return (
            self.uses_complement_invoice
            and self.ci_moment_of_creation == "cloud_spreadsheet"
        )

    def _product_ids_domain(self):
        return [
            ("is_fuel", "=", True),
        ]


    ci_product_ids = fields.Many2many(
        comodel_name="product.product", string="Products", domain=_product_ids_domain, store=True
    )
    ci_amount = fields.Selection(
        [("pump", "Pump"), ("manual", "Manual")], string="Amount for products"
    )
    #TODO: Manual -> elegir lista de precios
    #TODO: # crear turnos delimitando por fecha de inicio/ final
    # d:
    ci_restricts_liters = fields.Boolean()
    ci_liter_max_amount = fields.Float(
        string="Max liters per invoice",
        default=100.0,
        help="Quantity (liters / m3) per voucher since there are limitations in the south of the country"
            "that sales to the final consumer must not exceed 100 litres.",
    )
    uses_complement_credit_note = fields.Boolean()

    creates_ci_in_pos = fields.Boolean()
    creates_ci_in_cloud = fields.Boolean()

    @api.onchange('ci_moment_of_creation')
    def _onchange_ci_moment_of_creation(self):
        if self.ci_moment_of_creation in ['cloud_spreadsheet']:
            self.creates_ci_in_cloud = True
            self.creates_ci_in_pos = False
        if self.ci_moment_of_creation in ['pos_closing','pos_spreadsheet']:
            self.creates_ci_in_pos = True
            self.creates_ci_in_cloud = False
    # ----------
