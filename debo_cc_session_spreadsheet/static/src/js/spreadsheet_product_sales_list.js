odoo.define(
    "debo_cc_session_spreadsheet.spreadsheet_product_sales_list",
    (require) => {
        "use strict";

        require("web.dom_ready");
        const ajax = require("web.ajax");
        const Widget = require("web.AbstractField");
        const registry = require("web.field_registry");

        const getProductSalesList = (spreadsheetId) => {
            const tableBody = document.querySelector("#productSalesList");
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
                    const list = JSON.parse(response);
                    tableBody.innerHTML = "";
                    list.forEach((row) => {
                        document
                            .querySelector("#productSalesList")
                            .insertAdjacentHTML(
                                "afterbegin",
                                `<tr>
                                    <td>${row.invoice}</td>
                                    <td>${row.product}</td>
                                    <td>${row.quantity}</td>
                                    <td>$ ${row.price_unit},00</td>
                                    <td>$ ${row.price_total},00</td>
                                </tr>`
                            );
                    });
                }
            });
        };

        const SpreadsheetProductSalesList = Widget.extend({
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
                await waitForElm("#productSalesList");
                getProductSalesList(this.record.res_id);
            },

            isSet() {
                return true;
            },
        });

        registry.add(
            "spreadsheet_product_list_data",
            SpreadsheetProductSalesList
        );
    }
);
