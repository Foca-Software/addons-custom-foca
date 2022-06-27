def check_missing_complement_invoice(spreadsheet, env):
    """
    Check if there are missing complement invoices in the spreadsheet
    """

    # Get the list of fuel products and cubic meters sold
    fuel_move_ids = spreadsheet.session_id.mapped("fuel_move_ids")
    products = fuel_move_ids.mapped("product_id")
    fuel_sales = {}
    for product in products:
        fuel_sales[product.display_name] = sum(
            fuel_move_ids.filtered(
                lambda x, product=product: x.product_id == product
            ).mapped("cubic_meters")
        )

    # Update the amounts subtracting invoices
    invoices = spreadsheet.session_id.mapped("invoice_ids")
    for key, value in fuel_sales.items():
        for invoice in invoices:
            invoice_lines = invoice.invoice_line_ids.filtered(
                lambda x, key=key: x.name == key
            )
            if invoice_lines:
                fuel_sales[key] -= invoice_lines.cubic_meters
                break

    # Update the amounts subtracting other dispatches
    other_dispatches = spreadsheet.session_id.mapped("other_dispatch_line_ids")
    for key, value in fuel_sales.items():
        for other_dispatch in other_dispatches:
            if other_dispatch.name == key:
                fuel_sales[key] -= other_dispatch.product_uom_qty

    return True
