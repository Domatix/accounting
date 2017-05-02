# -*- coding: utf-8 -*-
###############################################################################
#    Module created by domatix
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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


class iva_record_wizzard(models.TransientModel):
    _name = 'dx_iva_record.iva_record_wizard'

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
    date_start = fields.Date(
        string='Start date')
    date_end = fields.Date(
        string='End date')

    period_from = fields.Many2one('account.period', 'Start Period',
                                  required=True)
    period_to = fields.Many2one('account.period', 'End Period', required=True)
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear', 'Fiscal Year', required=True)
    display_zero = fields.Boolean('Display Zero acc')

    partner_ids = fields.Many2many(comodel_name='res.partner',
                                   string='Partner',
                                   help='Déjelo vacío para todas las empresas')

    partner_type = fields.Selection(
        [('client', 'Cliente'), ('supplier', 'Proveedor')],
        string='Tipo de factura',
        help='Déjelo vacío para todos los tipos de factura')

    @api.onchange('period_from')
    def _onchange_period_from(self):
        self.date_start = self.period_from.date_start

    @api.onchange('period_to')
    def _onchange_period_to(self):
        self.date_end = self.period_to.date_stop

    def print_report(self, cr, uid, ids, context=None):

        if context is None:
            context = {}

        data = self.read(cr, uid, ids)[0]
        context['data_report'] = data

        report = 'dx_iva_record.report_iva_record'
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


iva_record_wizzard()
