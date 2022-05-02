odoo.define(
    "debo_cc_session_spreadsheet.spreadsheet_fuel_detailed_list",
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

        const create_fuels_table_content = (data) => {
            const fuelDetailed = document.querySelector("#fuelsDetailedTable");
            for (const fuel in data.fuels) {
                fuelDetailed.insertAdjacentHTML(
                    "beforeend",
                    `<tr>
                        <td colspan="8" class="font-weight-bold">${fuel}</td>
                    </tr>`
                );
                data.fuels[fuel].forEach((pump) => {
                    fuelDetailed.insertAdjacentHTML(
                        "beforeend",
                        `<tr>
                            <td class="text-center">
                                ${formant_currency(pump.price)}
                            </td>
                            <td class="text-center">${pump.id_debo}</td>
                            <td class="text-center">${pump.code}</td>
                            <td class="text-center">${pump.initial_qty}</td>
                            <td class="text-center">${pump.final_qty}</td>
                            <td class="text-center">${pump.manual_qty}</td>
                            <td class="text-center">${pump.cubic_meters}</td>
                            <td class="text-center">
                                ${formant_currency(pump.amount)}
                            </td>
                        </tr>`
                    );
                });
            }
        };

        const getFuels = (spreadsheetId) => {
            ajax.rpc(
                "/web/dataset/call_kw/cash.control.session.spreadsheet/get_session_fuel_detailed_list",
                {
                    model: "cash.control.session.spreadsheet",
                    method: "get_session_fuel_detailed_list",
                    args: [spreadsheetId],
                    kwargs: {},
                }
            ).then((response) => {
                if (response) {
                    const data = JSON.parse(response);
                    create_fuels_table_content(data);
                }
            });
        };

        const SpreadsheetFuelDetailedList = Widget.extend({
            template:
                "debo_cc_session_spreadsheet.fuel_detailed_list_widget_template",

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
                await waitForElm("#fuelsDetailedTable");
                getFuels(this.record.res_id);
            },

            isSet() {
                return true;
            },
        });

        registry.add(
            "spreadsheet_fuel_detailed_list",
            SpreadsheetFuelDetailedList
        );
    }
);
