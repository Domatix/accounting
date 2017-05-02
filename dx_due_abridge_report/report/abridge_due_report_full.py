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

from openerp.report import report_sxw
from openerp.osv import osv
from datetime import datetime, timedelta
import time


class abridge_due_report_full(report_sxw.rml_parse):
    _name = 'report.dx_due_abridge_report.abridge_due_report_full'

    def __init__(self, cr, uid, name, context):
        super(abridge_due_report_full, self).__init__(
            cr, uid, name, context=context)

        self.context = context
        user = self.pool.get('res.users').browse(cr, uid, uid)
        self.company = user.company_id
        self.lang = user.lang
        self.localcontext.update({
            'lang': self.lang,
            'get_data': self.get_data,
            'get_dates': self.get_dates,
            'daterange': self.daterange,
            'get_filter': self.get_filter,
            'get_summary': self.get_summary,
        })

    def get_filter(self):
        payment_mode = self.context['data_report']['payment_mode']
        aux = ['', ' NO conciliados', ' Conciliados']
        reconcile = aux[int(self.context['data_report']['reconcile'])]
        typeOf = 'Cobros' if self.context['data_report'][
            'payment_type'] == '0' else 'Pagos'
        res = typeOf + reconcile + ' filtrados por'
        date_to = datetime.strptime(
            self.context['data_report'].get('date_to'), '%Y-%m-%d')
        date_from = datetime.strptime(
            self.context['data_report'].get('date_from'), '%Y-%m-%d')
        res += ' fecha: desde ' + \
            date_from.strftime('%d/%m/%Y') + ' hasta ' + \
            date_to.strftime('%d/%m/%Y')
        if payment_mode:
            res += ' y modo de pago: ' + payment_mode[1]
        return res

    def daterange(self, start_date, end_date):
        for n in range(int((end_date - start_date).days)):
            yield start_date + timedelta(n)

    def get_dates(self):
        reconcile = self.context['data_report']['reconcile']
        res = []
        typeOf = 'receivable' if self.context['data_report'][
            'payment_type'] == '0' else 'payable'
        start_date = self.context['data_report'] and datetime.strptime(
            self.context['data_report'].get('date_from'), '%Y-%m-%d') or time
        end_date = self.context['data_report'] and datetime.strptime(
            self.context['data_report'].get('date_to'), '%Y-%m-%d') or time
        due_obj = self.get_lines(start_date.strftime('%m/%d/%Y'),
                                 end_date.strftime('%m/%d/%Y'))
        payment_mode = self.context['data_report']['payment_mode'] or 'empty'
        line_dates = []
        for line in due_obj:
            try:
                payment_mode_id = line.invoice.payment_mode_id.name
            except:
                payment_mode_id = line.invoice.payment_mode_id.sudo().name
            if payment_mode != 'empty':
                if payment_mode_id != payment_mode[1]:
                    continue
            if reconcile == '1':
                if line.reconcile_id:
                    continue
            elif reconcile == '2':
                if not line.reconcile_id:
                    continue
            try:
                line_dates.index(line.date_maturity)
                continue
            except:
                if line.account_id.type == typeOf:
                    line_dates.append(line.date_maturity)
        for date in self.daterange(start_date, end_date + timedelta(days=1)):
            if date.strftime('%Y-%m-%d') not in line_dates:
                continue
            res.append({'date': date.strftime('%Y-%m-%d'),
                        'format_date': date.strftime('%d/%m/%Y')})
        return res

    def get_data(self, date):
        reconcile = self.context['data_report']['reconcile']
        due_obj = self.get_lines(date)
        typeOf = 'receivable' if self.context['data_report'][
            'payment_type'] == '0' else 'payable'
        payment_mode = self.context['data_report']['payment_mode']
        res = []
        res_dict = {}
        for line in due_obj:
            if reconcile == '1':
                if line.reconcile_id:
                    continue
            elif reconcile == '2':
                if not line.reconcile_id:
                    continue
            if not line.account_id.type == typeOf:
                continue
            if payment_mode:
                if line.invoice.payment_mode_id.name != payment_mode[1]:
                    continue
            try:
                mode = line.invoice.payment_mode_id.name
            except:
                mode = line.invoice.payment_mode_id.sudo().name
            if not mode:
                mode = 'MODO DE PAGO NO DEFINIDO'
            if mode in res_dict:
                res_dict[mode][line.id] = {}
                res_dict[mode][line.id]['payment_mode'] = mode
                res_dict[mode][line.id]['total'] = line.debit - line.credit
                res_dict[mode][line.id][
                    'invoice'] = line.invoice.number or None
                res_dict[mode][line.id][
                    'maturity'] = datetime.strptime(line.date_maturity,
                                                    '%Y-%m-%d').strftime(
                                                    '%d/%m/%Y') or None
                res_dict[mode][line.id][
                    'account'] = line.invoice.partner_bank_id.name or None
                res_dict[mode][line.id]['ref'] = line.ref or None
                try:
                    res_dict[mode][line.id][
                        'partner_id'] = line.partner_id.name or None
                except:
                    res_dict[mode][line.id][
                        'partner_id'] = line.partner_id.sudo().name or None

            else:
                res_dict[mode] = {}
                res_dict[mode][line.id] = {}
                res_dict[mode][line.id][
                    'payment_mode'] = mode
                res_dict[mode][line.id][
                    'total'] = line.debit - line.credit
                res_dict[mode][line.id][
                    'invoice'] = line.invoice.number or None
                res_dict[mode][line.id][
                    'maturity'] = datetime.strptime(line.date_maturity,
                                                    '%Y-%m-%d').strftime(
                                                    '%d/%m/%Y') or None
                res_dict[mode][line.id][
                    'account'] = line.invoice.partner_bank_id.name or None
                res_dict[mode][line.id]['ref'] = line.ref or None
                try:
                    res_dict[mode][line.id][
                        'partner_id'] = line.partner_id.name or None
                except:
                    res_dict[mode][line.id][
                        'partner_id'] = line.partner_id.sudo().name or None
        for k in res_dict:
            res_aux = []
            for j in res_dict[k]:
                res_aux.append(res_dict[k][j])
            res.append(res_aux)
        return res

    def get_lines(self, date, dateRange=None):
        user_id = self.context['uid']
        company_id = self.pool.get('res.users').browse(
            self.cr, self.uid, [user_id]).company_id.id

        sql = "SELECT t.id FROM account_move_line as t"
        sql += " WHERE t.company_id = " + str(company_id)
        if dateRange is None:
            sql += " AND t.date_maturity = '" + str(date) + "'"
        else:
            sql += " AND t.date_maturity BETWEEN DATE('" + \
                date + "') AND DATE('" + dateRange + "')"
        sql += " ORDER BY t.date_maturity"
        sql += ";"
        self.cr.execute(sql)
        results = self.cr.fetchall()
        att_ids = [x[0] for x in results]
        due_obj = self.pool.get('account.move.line').browse(
            self.cr, self.uid, att_ids)
        return due_obj

    def get_summary(self):
        reconcile = self.context['data_report']['reconcile']
        start_date = self.context['data_report'] and datetime.strptime(
            self.context['data_report'].get('date_from'), '%Y-%m-%d') or time
        end_date = self.context['data_report'] and datetime.strptime(
            self.context['data_report'].get('date_to'), '%Y-%m-%d') or time
        due_obj = self.get_lines(start_date.strftime('%m/%d/%Y'),
                                 end_date.strftime('%m/%d/%Y'))
        typeOf = 'receivable' if self.context['data_report'][
            'payment_type'] == '0' else 'payable'
        payment_mode = self.context['data_report']['payment_mode']
        res = []
        res_dict = {}
        for line in due_obj:
            if reconcile == '1':
                if line.reconcile_id:
                    continue
            elif reconcile == '2':
                if not line.reconcile_id:
                    continue
            if not line.account_id.type == typeOf:
                continue
            if payment_mode:
                if line.invoice.payment_mode_id.name != payment_mode[1]:
                    continue
            try:
                    payment_mode_id = line.invoice.payment_mode_id.name
            except:
                payment_mode_id = line.invoice.payment_mode_id.sudo().name
            if not payment_mode_id:
                payment_mode_id = 'Modo de pago no definido'
            if payment_mode_id in res_dict:
                res_dict[payment_mode_id]['total'] += line.debit - line.credit
            else:
                res_dict[payment_mode_id] = {}
                res_dict[payment_mode_id]['payment_mode'] = payment_mode_id
                res_dict[payment_mode_id]['total'] = line.debit - line.credit
        for k in res_dict:
            res.append(res_dict[k])
        return res


# Clase parser para el wizard
class summary_parser(osv.AbstractModel):
    _name = 'report.dx_due_abridge_report.report_due_list_full'
    _inherit = 'report.abstract_report'
    _template = 'dx_due_abridge_report.report_due_list_full'
    _wrapped_report_class = abridge_due_report_full
