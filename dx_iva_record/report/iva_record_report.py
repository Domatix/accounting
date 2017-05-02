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

from openerp.report import report_sxw
from openerp.osv import osv
from datetime import datetime


class iva_record_report(report_sxw.rml_parse):
    _name = 'report.dx_iva_record.iva_record_report'

    def __init__(self, cr, uid, name, context):
        super(iva_record_report, self).__init__(
            cr, uid, name, context=context)

        self.context = context
        self.data_report = ('data_report' in context) and context[
            'data_report'] or None
        user = self.pool.get('res.users').browse(cr, uid, uid)
        self.company = user.company_id
        self.lang = user.lang
        self.localcontext.update({
            'lang': self.lang,
            'get_data': self.get_data,
            'get_format_date': self.get_format_date,
            'get_partner': self.get_partner,
        })

    def get_format_date(self, date_type):
        if date_type == 'start':
            date_start = self.data_report['date_start']
            start = datetime.strptime(date_start, '%Y-%m-%d')
            return start.strftime('%d/%m/%Y')
        elif date_type == 'end':
            date_end = self.data_report['date_end']
            end = datetime.strptime(date_end, '%Y-%m-%d')
            return end.strftime('%d/%m/%Y')

    def get_partner(self):
        if not self.data_report['partner_ids']:
            return "TODAS LAS EMPRESAS"
        else:
            partners = ""
            partner_id = self.pool.get('res.partner').\
                browse(self.cr,
                       self.uid, self.data_report['partner_ids'])

            if len(partner_id) < 2:
                return partner_id.name
            i = 1
            for partner in partner_id:
                if len(partner_id) == i:
                    partners += partner.name
                else:
                    partners += partner.name + ", "
                i = i+1
            return partners

    def get_data(self):

        company_id = self.pool.get('account.tax').\
         browse(self.cr,
                self.uid, [self.data_report['chart_tax_id'][0]]).company_id.id
        date_start = self.data_report['date_start'] or None
        date_end = self.data_report['date_end'] or None
        if self.data_report['partner_ids']:
            partner_ids = self.pool.get('res.partner').\
             browse(self.cr,
                    self.uid, self.data_report['partner_ids'])
        else:
            partner_ids = False

        sql = "SELECT t.id FROM account_invoice_tax as t"
        sql += " INNER JOIN account_invoice as i ON t.invoice_id = i.id"
        sql += " WHERE (i.state ='paid' or i.state = 'open')"
        sql += " AND i.company_id = " + str(company_id)
        sql += " AND (i.date_invoice BETWEEN DATE('" + \
            date_start + "') AND DATE('" + date_end + "'))"
        if partner_ids:
            sql += ' AND i.partner_id IN ('
            sql += ','.join(str(x.id) for x in partner_ids)
            sql += ')'
        if self.data_report['partner_type']:
            if self.data_report['partner_type'] == 'client':
                sql += " AND i.type = 'out_invoice'"
            elif self.data_report['partner_type'] == 'supplier':
                sql += " AND i.type = 'in_invoice'"
        sql += " ORDER BY i.date_invoice ASC"
        sql += ";"
        self.cr.execute(sql)
        results = self.cr.fetchall()
        att_ids = [x[0] for x in results]
        invoice_tax_obj = self.pool.get(
            'account.invoice.tax').browse(self.cr, self.uid, att_ids)
        res = []
        res_dict = {}
        for tax in invoice_tax_obj:
            if tax.name in res_dict:
                if tax.id not in res_dict[tax.name]:
                    res_dict[tax.name][tax.id] = {}

                res_dict[tax.name][tax.id][
                    'name'] = tax.name

                res_dict[tax.name][tax.id][
                    'fechaAsiento'] = datetime.strptime(
                    tax.invoice_id.move_id.date,
                    '%Y-%m-%d').strftime('%d/%m/%Y')

                res_dict[tax.name][tax.id][
                    'cuenta'] = tax.invoice_id.account_id.display_name.split(
                    ' ')[0] or tax.invoice_id.account_id.display_name

                try:
                    res_dict[tax.name][tax.id][
                        'partner'] = tax.invoice_id.partner_id.display_name
                    res_dict[tax.name][tax.id][
                        'cif'] = tax.invoice_id.partner_id.vat
                except:
                    res_dict[tax.name][tax.id][
                        'partner'] = tax.invoice_id.partner_id.sudo().name

                    res_dict[tax.name][tax.id][
                        'cif'] = tax.invoice_id.partner_id.sudo().vat

                res_dict[tax.name][tax.id][
                    'factura'] = tax.invoice_id.display_name.split(' ')[0]

                res_dict[tax.name][tax.id][
                    'fecha'] = datetime.strptime(
                    tax.invoice_id.date_invoice,
                        '%Y-%m-%d').strftime('%d/%m/%Y')

                res_dict[tax.name][tax.id][
                    'base'] = tax.base_amount

                res_dict[tax.name][tax.id][
                    'cuota'] = tax.amount

                res_dict[tax.name][tax.id][
                    'total'] = tax.base_amount + tax.amount

                res_dict[tax.name][tax.id][
                    'totalFactura'] = tax.invoice_id.amount_total

            else:
                res_dict[tax.name] = {}
                res_dict[tax.name][tax.id] = {}

                res_dict[tax.name][tax.id][
                    'name'] = tax.name

                res_dict[tax.name][tax.id][
                    'fechaAsiento'] = datetime.strptime(
                    tax.invoice_id.move_id.date,
                    '%Y-%m-%d').strftime('%d/%m/%Y')

                res_dict[tax.name][tax.id][
                    'cuenta'] = tax.invoice_id.account_id.display_name.split(
                    ' ')[0] or tax.invoice_id.account_id.display_name
                try:
                    res_dict[tax.name][tax.id][
                        'partner'] = tax.invoice_id.partner_id.display_name

                    res_dict[tax.name][tax.id][
                        'cif'] = tax.invoice_id.partner_id.vat
                except:
                    res_dict[tax.name][tax.id][
                        'partner'] = tax.invoice_id.partner_id.sudo().name

                    res_dict[tax.name][tax.id][
                        'cif'] = tax.invoice_id.partner_id.sudo().vat

                res_dict[tax.name][tax.id][
                    'factura'] = tax.invoice_id.display_name.split(' ')[0]

                res_dict[tax.name][tax.id][
                    'fecha'] = datetime.strptime(
                    tax.invoice_id.date_invoice,
                    '%Y-%m-%d').strftime('%d/%m/%Y')

                res_dict[tax.name][tax.id][
                    'base'] = tax.base_amount

                res_dict[tax.name][tax.id][
                    'cuota'] = tax.amount

                res_dict[tax.name][tax.id][
                    'total'] = tax.base_amount + tax.amount

                res_dict[tax.name][tax.id][
                    'totalFactura'] = tax.invoice_id.amount_total

        for k in res_dict:
            res_aux = []
            for j in res_dict[k]:
                res_aux.append(res_dict[k][j])
            res_aux = sorted(res_aux, key=lambda elem: elem['fechaAsiento'])
            res.append(res_aux)

        return res


# Wizard Parser
class record_parser(osv.AbstractModel):
    _name = 'report.dx_iva_record.report_iva_record'
    _inherit = 'report.abstract_report'
    _template = 'dx_iva_record.report_iva_record'
    _wrapped_report_class = iva_record_report
