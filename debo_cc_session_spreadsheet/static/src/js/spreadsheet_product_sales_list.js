odoo.define(
    "debo_cc_session_spreadsheet.spreadsheet_product_sales_list",
    (require) => {
        "use strict";

        require("web.dom_ready");
        const ajax = require("web.ajax");
        const registry = require("web.field_registry");
        const Widget = require("web.AbstractField");

        const formant_currency = (value) => {
            const formatter = new Intl.NumberFormat("es-AR", {
                style: "currency",
                currency: "ARS",
            });
            if (value === undefined) {
                return "";
            }
            return formatter.format(value);
        };

        const create_table_content = (data, table_body) => {
            let [qty_acc_check, total_acc_check, qty, total] = [0, 0, 0, 0];
            for (const product in data) {
                const row = data[product];
                qty_acc_check += row.product_qty_acc_check || 0;
                total_acc_check += row.product_total_acc_check || 0;
                qty += row.product_qty || 0;
                total += row.product_total || 0;
                table_body.insertAdjacentHTML(
                    "afterbegin",
                    `<tr>
                        <td>${product}</td>
                        <td class="text-center">
                            ${row.product_qty_acc_check ?? ""}
                        </td>
                        <td class="text-center">
                            ${formant_currency(row.product_total_acc_check)}
                        </td>
                        <td class="text-center">
                            ${row.product_qty ?? ""}
                        </td>
                        <td class="text-center">
                            ${formant_currency(row.product_total)}
                        </td>
                    </tr>`
                );
            }
            table_body.insertAdjacentHTML(
                "beforeend",
                `<tr class="text-center totals-row">
                    <td>Total</td>
                    <td>${qty_acc_check}</td>
                    <td>${formant_currency(total_acc_check)}</td>
                    <td>${qty}</td>
                    <td>${formant_currency(total)}</td>
                </tr>`
            );
        };

        const getProducts = (spreadsheetId) => {
            const products = document.querySelector("#productsTable");
            const fuelProducts = document.querySelector("#fuelProductsTable");

            ajax.rpc(
                "/web/dataset/call_kw/cash.control.session.spreadsheet/get_session_product_sales_list",
                {
                    model: "cash.control.session.spreadsheet",
                    method: "get_session_product_sales_list",
                    args: [spreadsheetId],
                    kwargs: {},
                }
            ).then((response) => {
                if (response) {
                    const data = JSON.parse(response);
                    products.innerHTML = "";
                    fuelProducts.innerHTML = "";
                    create_table_content(data.products, products);
                    create_table_content(data.fuels, fuelProducts);
                }
            });
        };

        const SpreadsheetProducts = Widget.extend({
            template:
                "debo_cc_session_spreadsheet.product_sales_list_widget_template",

            start() {
                this._super.apply(this, arguments);
                this.renderList();
            },

            async renderList() {
                const waitForElm = async (selector) => {
                    return new Promise((resolve) => {
                        if (document.querySelector(selector)) {
                            return resolve(document.querySelector(selector));
                        }

                        const observer = new MutationObserver((mutations) => {
                            if (document.querySelector(selector)) {
                                resolve(document.querySelector(selector));
                                observer.disconnect();
                            }
                        });

                        observer.observe(document.body, {
                            childList: true,
                            subtree: true,
                        });
                    });
                };
                await waitForElm("#productsTable");
                await waitForElm("#fuelProductsTable");
                getProducts(this.record.res_id);
            },

            isSet() {
                return true;
            },
        });

        registry.add("spreadsheet_product_list_data", SpreadsheetProducts);
    }
);
