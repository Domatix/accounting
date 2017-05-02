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


class iva_summary_report(report_sxw.rml_parse):
    _name = 'report.dx_iva_summary.iva_summary_report'

    def __init__(self, cr, uid, name, context):
        super(iva_summary_report, self).__init__(
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
        })

    def get_data(self, type):
        company_id = self.pool.get('account.tax').\
         browse(self.cr,
                self.uid, [self.data_report['chart_tax_id'][0]]).company_id.id
        start_period = self.data_report['period_from'][0]
        end_period = self.data_report['period_to'][0]
        date_start = str(self.pool.get('account.period').browse(
            self.cr, self.uid, [start_period]).date_start) or None
        date_end = str(self.pool.get('account.period').browse(
            self.cr, self.uid, [end_period]).date_stop) or None
        sql = "SELECT t.id FROM account_invoice_tax as t"
        sql += " INNER JOIN account_invoice as i ON t.invoice_id = i.id"
        sql += " WHERE (i.state ='paid' or i.state = 'open')"
        sql += " AND i.company_id = " + str(company_id)
        sql += " AND (i.date_invoice BETWEEN DATE('" + \
            date_start + "') AND DATE('" + date_end + "'))"
        if type not in ('other', 'retenciones'):
            if type == 'sale':
                sql += " AND i.type LIKE 'in_%'"
                sql += " AND t.name not like 'Exento%' AND \
                         t.name not like '%Retencion%'"
            if type == 'purchase':
                sql += " AND i.type LIKE 'out_%'"
                sql += " AND t.name not like 'Exento%' AND \
                         t.name not like '%Retencion%'"
        if type == 'retenciones':
            sql += " AND t.name like '%Retencion%'"
        if type == 'other':
            sql += " AND t.name like '%Exento%'"
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
                res_dict[tax.name]['base'] += tax.base_amount
                res_dict[tax.name]['cuota'] += tax.tax_amount
                res_dict[tax.name]['total'] += tax.base_amount + tax.tax_amount
            else:
                res_dict[tax.name] = {}
                res_dict[tax.name]['name'] = '-' + tax.name
                res_dict[tax.name]['base'] = tax.base_amount
                res_dict[tax.name]['cuota'] = tax.tax_amount
                res_dict[tax.name]['total'] = tax.base_amount + tax.tax_amount
        for k in res_dict:
            res.append(res_dict[k])
        return res


# Clase parser para el wizard
class summary_parser(osv.AbstractModel):
    _name = 'report.dx_iva_summary.report_iva_summary'
    _inherit = 'report.abstract_report'
    _template = 'dx_iva_summary.report_iva_summary'
    _wrapped_report_class = iva_summary_report
