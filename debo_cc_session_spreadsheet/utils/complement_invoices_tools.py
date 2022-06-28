def check_fuel_sales_conciliation(spreadsheet):
    """
    Check if there are missing complement invoices in the spreadsheet
    """
    # Get the list of Fuel Products and their corresponding cubic meters sold
    fuel_move_ids = spreadsheet.session_id.mapped("fuel_move_ids")
    products = fuel_move_ids.mapped("product_id")
    fuel_sales = {}
    for product in products:
        fuel_sales[product.display_name] = sum(
            fuel_move_ids.filtered(
                lambda x, product=product: x.product_id == product
            ).mapped("cubic_meters")
        )

    # Update the amounts subtracting INVOICES
    invoices = spreadsheet.session_id.mapped("invoice_ids")
    for key in fuel_sales:
        invoice_lines = invoices.mapped("invoice_line_ids").filtered(
            lambda x, key=key: x.name == key
        )
        if invoice_lines:
            fuel_sales[key] -= round(sum(invoice_lines.mapped("quantity")), 4)

    # Update the amounts subtracting OTHER DISPATCHES
    other_dispatches = spreadsheet.session_id.mapped("other_dispatch_line_ids")
    for key in fuel_sales:
        for other_dispatch in other_dispatches:
            if other_dispatch.name == key:
                fuel_sales[key] -= other_dispatch.product_uom_qty

    # Update the amounts subtracting PUMP TESTS
    pump_tests = spreadsheet.session_id.mapped("pump_test_line_ids")
    for key in fuel_sales:
        for pump_test in pump_tests:
            if pump_test.name == key:
                fuel_sales[key] -= pump_test.product_uom_qty

    return fuel_sales
