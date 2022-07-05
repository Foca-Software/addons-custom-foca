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
                let [qty, total] = [0, 0];
                data.fuels[fuel].forEach((pump) => {
                    qty += pump.cubic_meters || 0;
                    total += pump.amount || 0;
                    fuelDetailed.insertAdjacentHTML(
                        "beforeend",
                        `<tr id=${pump.id}>
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
                            <td class="text-center">
                            <button class="edit-pump-button btn btn-default m-0 p-0" data-toggle="modal" 
                                data-target="#editPumpModal"
                                data-id=${pump.id}
                                data-price=${formant_currency(pump.price)}
                                data-id_debo=${pump.id_debo}
                                data-code=${pump.code}
                                data-initial_qty=${pump.initial_qty}
                                data-final_qty=${pump.final_qty}
                                data-cubic_meters=${pump.cubic_meters}
                                data-amount=${formant_currency(pump.amount)}
                            ><i class="fa fa-pencil-square"></i></button>
                            </td>
                        </tr>`
                    );
                });
                fuelDetailed.insertAdjacentHTML(
                    "beforeend",
                    `<tr class="text-center totals-fuel-row">
                        <td colspan="6" class="text-right">Total</td>
                        <td class="text-center">${qty.toFixed(2)}</td>
                        <td class="text-center">${formant_currency(total)}</td>
                    </tr>`
                );
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

            events: {
                "click .edit-pump-button": "editPump",
                "click .save-pump-button": "savePump",
            },

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

            editPump() {
                $("#editPumpModal").on("show.bs.modal", function (event) {
                    const button = $(event.relatedTarget);
                    const line_id = button.data("id");
                    const price = button.data("price");
                    const id_debo = button.data("id_debo");
                    const code = button.data("code");
                    const initial_qty = button.data("initial_qty");
                    const final_qty = button.data("final_qty");
                    const cubic_meters = button.data("cubic_meters");
                    const amount = button.data("amount");

                    const modal = $(this);
                    modal.find("#modalTitleInfo").text(id_debo + " - " + code);
                    modal.find(".modal-body #line_id").val(line_id);
                    modal.find(".modal-body #price").val(price);
                    modal.find(".modal-body #initial_qty").val(initial_qty);
                    modal.find(".modal-body #final_qty").val(final_qty);
                    modal.find(".modal-body #cubic_meters").val(cubic_meters);
                    modal.find(".modal-body #amount").val(amount);

                    const initial_qtyInput =
                        document.querySelector("#initial_qty");
                    const final_qtyInput = document.querySelector("#final_qty");
                    const cubic_metersInput =
                        document.querySelector("#cubic_meters");
                    const amountInput = document.querySelector("#amount");

                    initial_qtyInput.addEventListener("change", (event) => {
                        final_qtyInput.value =
                            Number(event.target.value) +
                            Number(cubic_metersInput.value);
                        amountInput.value = formant_currency(
                            Number(cubic_metersInput.value) *
                                Number(price.replace("$", "").replace(",", "."))
                        );
                    });

                    final_qtyInput.addEventListener("change", (event) => {
                        cubic_metersInput.value =
                            Number(event.target.value) -
                            Number(initial_qtyInput.value);
                        amountInput.value = formant_currency(
                            Number(cubic_metersInput.value) *
                                Number(price.replace("$", "").replace(",", "."))
                        );
                    });

                    cubic_metersInput.addEventListener("change", (event) => {
                        final_qtyInput.value =
                            Number(event.target.value) +
                            Number(initial_qtyInput.value);
                        amountInput.value = formant_currency(
                            Number(cubic_metersInput.value) *
                                Number(price.replace("$", "").replace(",", "."))
                        );
                    });
                });
            },

            savePump(e) {
                const id = document.querySelector("#line_id").value;
                const initial_qty =
                    document.querySelector("#initial_qty").value;
                const final_qty = document.querySelector("#final_qty").value;
                const cubic_meters =
                    document.querySelector("#cubic_meters").value;

                ajax.rpc(
                    "/web/dataset/call_kw/cash.control.session.spreadsheet/update_pump",
                    {
                        model: "cash.control.session.spreadsheet",
                        method: "update_pump",
                        args: [id, initial_qty, final_qty, cubic_meters],
                        kwargs: {},
                    }
                ).then((response) => {
                    if (response) {
                        const data = JSON.parse(response);
                        console.log(data);
                        if (data.success) {
                            // TODO: improve the row update to avoid this reload
                            document.location.reload(true);
                        }
                    }
                });
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
