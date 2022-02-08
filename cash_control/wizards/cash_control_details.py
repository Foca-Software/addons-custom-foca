# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class CashControlDetails(models.TransientModel):
    _name = 'cash.control.details.wizard'
    _description = 'Point of Sale Details Report'

    def _default_start_date(self):
        """ Find the earliest start_date of the latests sessions """
        # restrict to configs available to the user
        config_ids = self.env['cash.control.config'].search([]).ids
        # exclude configs has not been opened for 2 days
        self.env.cr.execute("""
            SELECT
            max(date_start) as start,
            config_id
            FROM cash_control_session
            WHERE config_id = ANY(%s)
            AND date_start > (NOW() - INTERVAL '2 DAYS')
            GROUP BY config_id
        """, (config_ids,))
        latest_start_dates = [res['start'] for res in self.env.cr.dictfetchall()]
        # earliest of the latest sessions
        return latest_start_dates and min(latest_start_dates) or fields.Datetime.now()

    start_date = fields.Datetime(required=True, default=_default_start_date)
    end_date = fields.Datetime(required=True, default=fields.Datetime.now)
    cash_control_config_ids = fields.Many2many('cash.control.config', 'cash_control_detail_configs',
        default=lambda s: s.env['cash.control.config'].search([]))

    @api.onchange('start_date')
    def _onchange_start_date(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            self.end_date = self.start_date

    @api.onchange('end_date')
    def _onchange_end_date(self):
        if self.end_date and self.end_date < self.start_date:
            self.start_date = self.end_date

    def generate_report(self):
        data = {'date_start': self.start_date, 'date_stop': self.end_date, 'config_ids': self.cash_control_config_ids.ids}
        return self.env.ref('cash_control.sale_details_report').report_action([], data=data)
