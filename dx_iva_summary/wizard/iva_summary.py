# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2015 Domatix (http://www.domatix.com)
#                       info <info@domatix.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, api


class iva_summary_wizzard(models.TransientModel):
    _name = 'dx_iva_summary.iva_summary_wizard'

    @api.multi
    def _get_tax(self):
        user = self.env['res.users'].browse(self._uid)
        taxes = self.env['account.tax.code'].search(
            [('parent_id', '=', False), ('company_id', '=',
                                         user.company_id.id)], limit=1)
        return taxes and taxes[0] or False

    chart_tax_id = fields.Many2one('account.tax.code', 'Chart of Tax',
                                   help='Select Charts of Taxes',
                                   required=True,
                                   domain=[('parent_id', '=', False)],
                                   default=_get_tax)
    period_from = fields.Many2one('account.period', 'Start Period',
                                  required=True)
    period_to = fields.Many2one('account.period', 'End Period', required=True)
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear', 'Fiscal Year', required=True)
    display_zero = fields.Boolean('Display Zero acc')

    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        context['data_report'] = data
        report = 'dx_iva_summary.report_iva_summary'
        datas = {
            'ids': [],
            'model': 'account.invoice',
            'form': data,
            'context': context,
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': report,
            'datas': datas,
            'context': context,
        }


iva_summary_wizzard()
