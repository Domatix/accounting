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
from openerp import models, fields, api, _
import time
from openerp.osv import osv
from StringIO import StringIO
import xlwt
from xlwt import Workbook, easyxf
from datetime import datetime
from openerp.exceptions import Warning
import base64


class xls_report(osv.osv):
    _name = "xls.report"
    name = fields.Char(
        string='Nombre')


class due_list_wizzard(models.TransientModel):
    _name = 'dx_due_abridge_report.abridge_due_wizard'

    date_from = fields.Date(string='date from', required=True,
                            default=lambda *a: time.strftime('%Y-%m-01'))
    date_to = fields.Date(string='date to', required=True,
                          default=lambda *a: time.strftime('%Y-%m-%d'))
    payment_type = fields.Selection([('0', 'Receivable'),
                                     ('1', 'Payable')],
                                    default='0',
                                    string='Due type',
                                    required=True)
    report_mode = fields.Selection([('0', 'Abridged'),
                                    ('1', 'Full')],
                                   default='0',
                                   string='Type of report',
                                   required=True)

    payment_mode = fields.Many2one('payment.mode', 'Payment mode',
                                   help='Select payment mode')

    file = fields.Binary(string='File')
    file_name = fields.Char(string='File Name', size=64)
    reconcile = fields.Selection([('0', 'All'),
                                 ('1', 'Unreconciled'),
                                 ('2', 'Reconciled')],
                                 default='0',
                                 string='State',
                                 required=True)

    @api.onchange('date_from', 'date_to')
    def _check_dates(self):
        if self.date_from > self.date_to:
            raise Warning(
                _("La fecha hasta debe ser mayor o igual que la fecha desde"))

    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(due_list_wizzard, self).default_get(
            cr, uid, fields, context=context)
        res.update({'file_name': 'Efectos Abreviados.xls'})
        if context.get('file'):
            res.update({'file': context['file']})
        return res

    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        data = self.read(cr, uid, ids)[0]
        file_name = 'Informe de efectos '
        context['data_report'] = data
        if data['report_mode'] == '0':
            file_name += 'abreviados de '
            report = 'dx_due_abridge_report.report_due_list_abridge'
        if data['report_mode'] == '1':
            file_name += ' de '
            report = 'dx_due_abridge_report.report_due_list_full'
        file_name += 'Cobros' if data['payment_type'] == '0' else 'Pagos'
        datas = {
            'ids': [],
            'model': 'account.move.line',
            'form': data,
            'context': context,
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': report,
            'name': file_name,
            'datas': datas,
            'context': context,
        }

    def get_data(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids)[0]
        reconcile = data['reconcile']
        typeOf = 'receivable' if data['payment_type'] == '0' else 'payable'
        payment_mode = data['payment_mode']
        user_id = context['uid']
        company_id = self.pool.get('res.users').browse(
            cr, uid, [user_id]).company_id.id
        atts = []
        atts.append(('date_maturity', '>=', data['date_from']))
        atts.append(('date_maturity', '<=', data['date_to']))
        atts.append(('company_id', '=', company_id))
        move_lines_ids = self.pool.get('account.move.line').\
            search(cr, uid, atts, order="date_maturity asc")
        move_lines = self.pool.get('account.move.line').browse(
            cr, uid, move_lines_ids)
        report_mode = data['report_mode']
        res_dict = {}
        for line in move_lines:
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
            date_maturity = line.date_maturity
            mode = line.invoice.payment_mode_id.name
            if not mode:
                mode = 'Modo de pago no definido'
            if report_mode == '0':
                if date_maturity in res_dict:
                    if mode in res_dict[date_maturity]:
                        res_dict[date_maturity][mode] += \
                            line.debit - line.credit
                    else:
                        res_dict[date_maturity][mode] = {}
                        res_dict[date_maturity][mode] = \
                            line.debit - line.credit
                else:
                    res_dict[date_maturity] = {}
                    res_dict[date_maturity][mode] = {}
                    res_dict[date_maturity][mode] =\
                        line.debit - line.credit
            else:
                if date_maturity in res_dict:
                    if line.id in res_dict[date_maturity]:
                        res_dict[date_maturity][line.id]['payment_mode'] = mode
                        res_dict[date_maturity][line.id][
                            'total'] = line.debit - line.credit
                        res_dict[date_maturity][line.id][
                            'invoice'] = line.invoice.number or None
                        res_dict[date_maturity][line.id][
                            'maturity'] = line.date_maturity or None
                        res_dict[date_maturity][line.id]['account'] = \
                            line.invoice.partner_bank_id.name or None
                        res_dict[date_maturity][line.id]['ref'] = \
                            line.ref or None
                        res_dict[date_maturity][line.id][
                            'partner_id'] = line.partner_id.name or None
                    else:
                        res_dict[date_maturity][line.id] = {}
                        res_dict[date_maturity][line.id]['payment_mode'] = mode
                        res_dict[date_maturity][line.id][
                            'total'] = line.debit - line.credit
                        res_dict[date_maturity][line.id][
                            'invoice'] = line.invoice.number or None
                        res_dict[date_maturity][line.id][
                            'maturity'] = line.date_maturity or None
                        res_dict[date_maturity][line.id]['account'] = \
                            line.invoice.partner_bank_id.name or None
                        res_dict[date_maturity][line.id]['ref'] = \
                            line.ref or None
                        res_dict[date_maturity][line.id][
                            'partner_id'] = line.partner_id.name or None
                else:
                    res_dict[date_maturity] = {}
                    res_dict[date_maturity][line.id] = {}
                    res_dict[date_maturity][line.id]['payment_mode'] = mode
                    res_dict[date_maturity][line.id][
                        'total'] = line.debit - line.credit
                    res_dict[date_maturity][line.id][
                        'invoice'] = line.invoice.number or None
                    res_dict[date_maturity][line.id][
                        'maturity'] = line.date_maturity or None
                    res_dict[date_maturity][line.id][
                        'account'] = line.invoice.partner_bank_id.name or None
                    res_dict[date_maturity][line.id]['ref'] = line.ref or None
                    res_dict[date_maturity][line.id][
                        'partner_id'] = line.partner_id.name or None
        return res_dict

    def write_xls(self, res_dict, wbk, mode):
        report_mode = mode
        data_d = res_dict
        sheet = wbk.add_sheet('Efectos abreviados', cell_overwrite_ok=True)
        xlwt.add_palette_colour("light_grey", 0x21)
        wbk.set_colour_RGB(0x21, 221, 221, 221)

        bold = easyxf(
            'font: height 210, name Calibri, bold on;')
        num = easyxf(num_format_str='_(#,##0.00_);(#,##0.00)')
        base = easyxf()

        if report_mode == '0':
            sheet.col(1).width = 256 * 70
            sheet.col(2).width = 256 * 15
            fila = 0
            sheet.write(fila, 0, 'Fecha', bold)
            sheet.write(fila, 1, 'Modo de pago', bold)
            sheet.write(fila, 2, 'Total', bold)
            fila += 1
            for k in sorted(data_d):
                date = datetime.strptime(k, '%Y-%m-%d').strftime('%d/%m/%Y')
                for payment in data_d[k]:
                    sheet.write(fila, 0, date, base)
                    sheet.write(fila, 1, payment, base)
                    sheet.write(fila, 2, data_d[k][payment], num)
                    fila += 1

        else:
            sheet.col(1).width = 256 * 70
            sheet.col(2).width = 256 * 20
            sheet.col(3).width = 256 * 50
            sheet.col(5).width = 256 * 70
            fila = 0
            sheet.write(fila, 0, 'Fecha', bold)
            sheet.write(fila, 1, 'Modo de pago', bold)
            sheet.write(fila, 2, 'Cuenta', bold)
            sheet.write(fila, 3, 'Factura', bold)
            sheet.write(fila, 4, 'Vencimiento', bold)
            sheet.write(fila, 5, 'Referencia', bold)
            sheet.write(fila, 6, 'Total', bold)
            fila += 1
            for k in sorted(data_d):
                date = datetime.strptime(k, '%Y-%m-%d').strftime('%d/%m/%Y')
                for line in data_d[k]:
                    date_m = datetime.strptime(data_d[k][line]['maturity'],
                                               '%Y-%m-%d').strftime('%d/%m/%Y')
                    sheet.write(fila, 0, date, num)
                    sheet.write(fila, 1, data_d[k][line]['payment_mode'], num)
                    sheet.write(fila, 2, data_d[k][line]['account'], num)
                    sheet.write(fila, 3, data_d[k][line]['partner_id'], num)
                    sheet.write(fila, 4, date_m, num)
                    sheet.write(fila, 5, data_d[k][line]['ref'], num)
                    sheet.write(fila, 6, data_d[k][line]['total'], num)
                    fila += 1

    def export_xls_payment(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids)[0]
        report_mode = data['report_mode']
        res_dict = self.get_data(cr, uid, ids, context)
        fl = StringIO()
        if context is None:
            context = {}
        wbk = Workbook(encoding='utf-8')
        self.write_xls(res_dict, wbk, report_mode)
        wbk.save(fl)
        fl.seek(0)
        buf = base64.encodestring(fl.read())
        ctx = dict(context)
        ctx.update({'file': buf})
        if context is None:
            context = {}
        data = {}
        res = self.read(cr, uid, ids, [], context=context)
        res = res and res[0] or {}
        data['form'] = res
        try:
            form_id = self.pool.get('ir.model.data').get_object_reference(
                cr, uid, 'report_xls', 'view_xls_file_form_view')[1]
        except ValueError:
            form_id = False
        return{
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'dx_due_abridge_report.abridge_due_wizard',
            'views': [(form_id, 'form')],
            'view_id': form_id,
            'target': 'new',
            'context': ctx,

        }


due_list_wizzard()
