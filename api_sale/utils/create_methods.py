from odoo.http import request
from odoo import fields, http, api
from datetime import datetime
import logging
from odoo.exceptions import AccessError, ValidationError

_logger = logging.getLogger(__name__)

DEBO_DATE_FORMAT = "%d/%m/%Y"
ADMIN_ID = 2

# public methods
def create_sale_order(user_id: int, data: dict) -> object or False:
    """
        Return list of sale.order object
    """
    sale_data = data.get("header")
    sale_order_ids = []
    sale_obj = request.env["sale.order"].with_user(user_id)
    sorted_lines = _sort_lines(data["lines"])
    fuel_lines = sorted_lines[0]
    non_fuel_lines = sorted_lines[1]
    if fuel_lines:
        fuel_order = _create_sale_order(sale_data, sale_obj)
        fuel_order._add_lines(fuel_lines)
        sale_order_ids.append(fuel_order)
    if non_fuel_lines:
        non_fuel_order = _create_sale_order(sale_data, sale_obj)
        non_fuel_order._add_lines(non_fuel_lines)
        sale_order_ids.append(non_fuel_order)
    return sale_obj.browse(order.id for order in sale_order_ids)


def confirm_or_unreserve_orders(sale_orders: object, user_id: int) -> object:
    picking_ids = (
        request.env["stock.picking"]
        .with_user(ADMIN_ID)
        .search([("sale_id", "in", sale_orders.ids)])
    )
    for picking in picking_ids:
        unreserve_required = any(line.product_id.is_fuel for line in picking.move_lines)
        if unreserve_required:
            picking.do_unreserve()
        else:
            try:
                picking.action_assign()
                picking.button_validate()
                wiz = (
                    request.env["stock.immediate.transfer"]
                    .with_user(user_id)
                    .create({"pick_ids": [(4, picking.id)]})
                )
                wiz.process()
            except Exception as e:
                _logger.error(e)
                continue  # TODO: handle this better
                # this means that something failed while confirming the picking / stock move
                # odoo response to this has not been specified
    return picking_ids


def create_invoices_from_sale(sale_orders: object, invoice_data: dict) -> object:
    invoice_ids = sale_orders._create_invoices()
    for invoice in invoice_ids:
        invoice.write(invoice_data)
        invoice.pay_now_journal_id = _check_pay_now_journal_ok(invoice)
    return invoice_ids


def create_payments_from_invoices(
    invoice_id: object,
    payment_data: dict,
    user_id: int,
) -> object:
    if not _payment_required(invoice_id, payment_data):
        return False
    context = _get_payment_context(invoice_id)
    payment_group = _create_payment_group(user_id, invoice_id, context)
    _check_multiple_payments_amount(payment_data)
    payments = _create_payments(
        payment_data,
        payment_group,
        invoice_id,
        user_id,
        context,
    )
    _logger.info(payments)
    _compute_and_post_payment(payment_group)
    return payment_group

def _compute_and_post_payment(payment_group: object) -> bool:
    payment_group._compute_payments_amount()
    payment_group._compute_matched_amounts()
    payment_group._compute_document_number()
    payment_group._compute_matched_amount_untaxed()
    payment_group._compute_move_lines()
    # payment compute methods
    for payment in payment_group.payment_ids:
        payment._onchange_partner_id()
        payment._compute_reconciled_invoice_ids()
        payment.post()
    payment_group.post()
    return True

# private methods
def _check_pay_now_journal_ok(invoice: object) -> int or False:
    if invoice.pay_now_journal_id:
        payment_methods = invoice.pay_now_journal_id.inbound_payment_method_ids
        payment_method = payment_methods.filtered(lambda x: x.code == "manual")
        # if it's not manual, will raise an error
        if not payment_method:
            return False
        return invoice.pay_now_journal_id.id


def _sort_lines(data: list) -> list:
    """
    return list of lists of dicts
    index 0 = lines where product_id is_fuel
    index 1 = lines where product_id not is_fuel
    """
    fuel_lines = []
    non_fuel_lines = []
    product_obj = request.env["product.product"].with_user(ADMIN_ID)
    for line in data:
        is_fuel = product_obj.browse(line["product_id"]).is_fuel
        if is_fuel:
            fuel_lines.append(line)
        else:
            non_fuel_lines.append(line)
    return [fuel_lines, non_fuel_lines]


def _create_sale_order(sale_data: dict, sale_obj: object) -> object:
    date_order = datetime.strptime(sale_data["date_order"], DEBO_DATE_FORMAT)
    sale_order = sale_obj.create(
        {
            "partner_id": sale_data.get("partner_id"),
            "date_order": date_order or datetime.now(),
            "state": "draft",
        }
    )
    sale_order.onchange_partner_id()
    sale_order.onchange_user_id()

    sale_order.write(
        {
            "partner_invoice_id": sale_data.get("partner_invoice_id")
            or sale_order.partner_invoice_id.id,
            "partner_shipping_id": sale_data.get("partner_shipping_id")
            or sale_order.partner_shipping_id.id,
            "pricelist_id": sale_data.get("pricelist_id") or sale_order.pricelist_id.id,
        }
    )
    return sale_order


def _payment_required(invoice: object, payment_data: dict) -> bool:
    invoice_is_paid = invoice.invoice_payment_state == "paid"
    return payment_data or not invoice_is_paid


def _create_payment_group(
    user_id: int, invoice_id: object, context: dict
) -> object or False:
    acc_pay_group_obj = request.env["account.payment.group"].with_user(user_id)
    apg_vals_list = {
        "partner_id": context["default_partner_id"],
        "to_pay_move_line_ids": context["to_pay_move_line_ids"],
        "company_id": context["default_company_id"],
        "state": "draft",
        "partner_type": "customer",
    }
    payment_group = acc_pay_group_obj.with_context(
        active_ids=invoice_id.ids, active_model="account.move"
    ).create(apg_vals_list)
    return payment_group


def _check_multiple_payments_amount(payment_data: list) -> bool:
    """
    Raise exception if multiple payment methods are found but amount is missing
    """
    if len(payment_data) > 1:
        for payment_method in payment_data:
            if "amount" not in payment_method.keys():
                raise ValidationError(
                    """
                Payment data is not valid. 
                If multiple payment methods are used, amount must be provided for each payment method
                """
                )
    return True


def _create_payments(
    payment_data: list,
    payment_group: object,
    invoice_id: object,
    user_id: int,
    context: dict,
) -> object:
    """
    return :: account.payment list
    """
    payment_list = []
    acc_payment_obj = request.env["account.payment"].with_user(user_id)
    for payment in payment_data:
        payment_vals = {
            # inmutable fields
            "partner_id": invoice_id.partner_id.id,
            "payment_type": "inbound",
            "partner_type": "customer",
            "payment_group_id": payment_group.id,
            "amount": payment.get("amount")
            or acc_payment_obj._compute_payment_amount(
                invoice_id,
                invoice_id.currency_id,
                invoice_id.journal_id,
                invoice_id.invoice_date,
            ),
            # payment_data dependant fields
            "journal_id": payment["journal_id"],
            "payment_method_id": payment.get("payment_method_id"),
            "company_id": invoice_id.company_id,
        }
        payment_context = {
            "active_ids": invoice_id.ids,
            "active_model": "account.move",
            "to_pay_move_line_ids": context["to_pay_move_line_ids"],
        }
        payment_context.update(context)
        payment_vals.update(_get_additional_payment_vals(payment,payment_group))
        acc_payment = acc_payment_obj.with_context(payment_context).create(payment_vals)
        payment_list.append(acc_payment)

    return payment_list


def _get_additional_payment_vals(payment: dict, payment_group: object) -> dict:
    """
    return dictionary with fields necessary for different types of payments
    """
    default_date = datetime.now()
    default_date_str = datetime.strftime(default_date,DEBO_DATE_FORMAT)
    check_vals = {
        "check_number": payment.get("check_number"),
        "check_name": _get_name_from_number(payment.get("check_number")),
        "check_bank_id": payment.get("check_bank_id"),
        "check_issue_date": datetime.strptime(
            payment.get("check_issue_date",default_date_str), DEBO_DATE_FORMAT
        ),
        "check_owner_vat": payment_group.partner_id.vat,
        "check_owner_name": payment_group.partner_id.name,
    }
    credit_debit_vals = {
        "card_id": payment.get("card_id", False),  # computable?
        "instalment_id": payment.get("instalment_id", False),  # computable?
        # ------------------------------------------------------
        "tiket_number": payment.get("ticket_number", False),
        "card_number": payment.get("card_number", False),
        "lot_number": payment.get("lot_number", False),
    }
    new_payment_vals = {
        "received_third_check" : check_vals,
        "inbound_debit_card" : credit_debit_vals,
        "inbound_credit_card" : credit_debit_vals,
        False : {}, #in case _get_payment_method_code returns False
    }
    journal_id = payment.get("journal_id")
    payment_journal_code = _get_payment_method_code(journal_id)
    return new_payment_vals[payment_journal_code]


def _get_payment_method_code(journal_id: int) -> str:
    account_journal_obj = request.env["account.journal"].with_user(ADMIN_ID)
    payment_journal = account_journal_obj.browse(journal_id)
    payment_method = (
        payment_journal.inbound_payment_method_ids[0]
        if len(payment_journal.inbound_payment_method_ids) > 0
        else False
    )
    if not payment_method:
        raise ValidationError("Payment Journal has no valid Inbound Payment Methods")
    return payment_method.code


def _get_payment_context(invoice_id: object) -> dict:
    # execute 'register payment' button to get context values
    wizard = invoice_id.with_context(
        active_ids=invoice_id.ids,
        active_model="account.move",
    ).action_account_invoice_payment_group()
    context = wizard["context"]
    return context


def _inbound_check_codes():
    return ["received_third_check"]


def _inbound_card_codes():
    return ["inbound_debit_card", "inbound_credit_card"]


def _get_name_from_number(number):
    padding = 8
    if len(str(number)) > padding:
        padding = len(str(number))
    return "%%0%sd" % padding % number



def create_invoice(user_id: int, data: dict) -> dict:
    try:
        account_obj = request.env["account.move"].with_user(user_id)
        move_line_obj = request.env["account.move.line"].with_user(user_id)
    except AccessError as e:
        _logger.error(e.args)
        return {"invoice_id": 0, "status": "error", "error": e.args}
    invoice_data = data["header"]
    try:
        invoice_id = account_obj.create(
            {
                "partner_id": invoice_data["partner_id"],
                "partner_shipping_id": invoice_data["partner_shipping_id"],
                "ref": invoice_data["ref"],
                "invoice_date": datetime.strptime(
                    invoice_data["invoice_date"], DEBO_DATE_FORMAT
                ),
                "journal_id": invoice_data["journal_id"],
                "l10n_latam_document_type_id": invoice_data[
                    "l10n_latam_document_type_id"
                ],
                "company_id": invoice_data["company_id"],
                "currency_id": invoice_data["currency_id"],
                # not sent in the data
                "type": "out_invoice",
                "state": "draft",
            }
        )

    except ValueError as e:
        _logger.error(e.args)
        return {"invoice_id": 0, "status": "error", "error": e.args}
    try:
        created_invoice = account_obj.browse(invoice_id.id)
        for line in data["invoice_line_ids"]:
            created_invoice.invoice_line_ids = [
                (
                    0,
                    0,
                    {
                        "product_id": line["product_id"],
                        "name": line["name"],
                        "account_id": line["account_id"],
                        "quantity": line["quantity"],
                        "product_uom_id": line["product_uom_id"],
                        "price_unit": line["price_unit"],
                        "tax_ids": [(6, 0, [line["tax_ids"]])],
                        "exclude_from_invoice_tab": False,
                    },
                )
            ]
    except ValueError as e:
        _logger.error(e.args)
        return {
            "invoice_id": invoice_id.id,
            "status": "error",
            "message": "Error creating invoice",
        }

    return {
        "invoice_id": invoice_id.id,
        "status": "success",
        "message": "Invoice created successfully",
    }


def verify_user(user: str, password: str) -> int:
    user = (
        request.env["res.users"]
        .with_user(1)
        .search([("login", "=", user), ("password", "=", password)])
    )
    if user:
        return user.id
    else:
        return 0


def check_required_fields(data: dict, move_type: int) -> list or False:
    """ """
    # move_type = str(move_type)
    required_fields = {
        101: [
            # "partner_id",
            # "partner_shipping_id",
            # "partner_invoice_id",
            "date_order",
            # "pricelist_id",
        ],
        102: [
            "partner_id",
            "partner_shipping_id",
            "ref",
            "invoice_date",
            "journal_id",
            "l10n_latam_document_type",
            "currency_id",
        ],
    }
    required_line_fields = {
        101: [
            "product_id",
            # "product_template_id",
            # "name",
            # "product_uom_qty",
            # "product_uom",
            # "price_unit",
            # "tax_id",
        ],
        102: [
            "product_id",
            "name",
            "account_id",
            "quantity",
            "product_uom_id",
            "price_unit",
            "tax_ids",
        ],
    }
    missing_fields = []
    for field in required_fields[move_type]:
        if not data["header"].get(field, False):
            missing_fields.append(field)
    for field in required_line_fields[move_type]:
        for line in data["lines"]:
            if not line.get(field, False):
                missing_fields.append(field)

    return missing_fields if missing_fields else False

