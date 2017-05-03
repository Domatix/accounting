# -*- coding: utf-8 -*-
###############################################################################
#    Module created by domatix
#    OpenERP, Open Source Management Solution
#
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
import time
from datetime import datetime
from datetime import timedelta
from openerp.report import report_sxw
from openerp.osv import osv
from openerp.tools.translate import _


class signings_report_employee(report_sxw.rml_parse):
    _name = 'report.dx_order_signings_report.signings_report_employee'

    def __init__(self, cr, uid, name, context):
        super(signings_report_employee, self).__init__(
                                                cr, uid, name, context=context)
        self.context = context
        self.data_report = context['data_report'] or None
        user = self.pool.get('res.users').browse(cr, uid, uid)
        self.company = user.company_id
        self.lang = user.lang
        self.localcontext.update({
            'time': time,
            'lang': self.lang,
            'get_period': self.get_period,
            'get_employee': self.get_employee,
            'get_employees': self.get_employees,
            'get_order': self.get_order,
            'has_signings': self.has_signings,
            'get_signings': self.get_signings,
            'get_total_signings': self.get_total_signings,
        })

    def get_period(self):
        start_date = self.data_report and datetime.strptime(
                     self.data_report['start_date'], '%Y-%m-%d') or time
        end_date = self.data_report and datetime.strptime(
                   self.data_report['end_date'], '%Y-%m-%d') or time
        res = start_date.strftime('%d/%m/%Y')
        res += ' - '
        res += end_date.strftime('%d/%m/%Y')
        return res

    def get_employee(self):
        emp_obj = self.pool.get('hr.employee')
        name = _('All employees')
        employee = self.data_report['employee_id'] and emp_obj.browse(
            self.cr, self.uid, self.data_report['employee_id'][0]) or None
        if employee:
            name = '[' + employee[0].internal_code + '] ' + employee[0].name
        return name

    def get_employees(self):
        emp_obj = self.pool.get('hr.employee')
        emp_ids = self.data_report and self.data_report['employee_id'] and [
         self.data_report['employee_id'][0]] or emp_obj.search(
                self.cr, self.uid, [], order='name')
        aux = []
        for empl in emp_ids:
            aux.append(empl)
            if not self.has_signings(empl):
                aux.remove(empl)
        res = emp_obj.browse(self.cr, self.uid, aux)
        return res

    def has_signings(self, empl):
        prod = self.pool.get('mrp.production.signing')
        start_date = self.data_report and datetime.strptime(
            self.data_report['start_date'], '%Y-%m-%d') or time
        end_date = self.data_report and datetime.strptime(
            self.data_report['end_date'], '%Y-%m-%d') or time
        emp_obj = self.pool.get('hr.employee')
        employee = self.data_report and self.data_report[
            'employee_id'] and emp_obj.browse(
                self.cr, self.uid, self.data_report['employee_id'][0]) or None
        order = self.data_report and self.data_report[
            'order_id'] and prod.browse(
                self.cr, self.uid, self.data_report['order_id'][0]) or None
        sql = " SELECT s.id, e.name_related , s.date_start, s.date_finished, \
               p.name "
        sql += "FROM mrp_production_signing s "
        sql += "INNER JOIN hr_employee e ON s.employee_id=e.id "
        sql += "INNER JOIN mrp_production p ON p.id = s.production_id "
        sql += "WHERE DATE(s.date_start)>='" + str(start_date) + "'"
        sql += "AND DATE(s.date_start)<='" + str(end_date) + "'"
        sql += " AND e.id=" + str(empl) + " "
        if order:
            sql += " and p.id=" + str(order.id) + " "
        if employee:
            sql += "ORDER BY s.date_start ,e.name_related "
        self.cr.execute(sql)
        results = self.cr.fetchall()
        att_ids = [x[0] for x in results]
        return len(att_ids) > 0

    def get_order(self):
        prod = self.pool.get('mrp.production.signing')
        name = _('All Orders')
        order = self.data_report and self.data_report[
            'order_id'] and prod.browse(
                self.cr, self.uid, self.data_report['order_id'][0]) or None
        if order:
            name = self.data_report['order_id'][1]
        return name

    def daterange(self, start_date, end_date):
        for n in range(int((end_date - start_date).days)):
            yield start_date + timedelta(n)

    def get_signings(self, empl):
        prod = self.pool.get('mrp.production.signing')
        start_date = self.data_report and datetime.strptime(
            self.data_report['start_date'], '%Y-%m-%d') or time
        end_date = self.data_report and datetime.strptime(
            self.data_report['end_date'], '%Y-%m-%d') or time
        emp_obj = self.pool.get('hr.employee')
        employee = self.data_report and self.data_report[
            'employee_id'] and emp_obj.browse(
                self.cr, self.uid, self.data_report['employee_id'][0]) or None
        order = self.data_report and self.data_report[
            'order_id'] and prod.browse(
                self.cr, self.uid, self.data_report['order_id'][0]) or None
        sql = "SELECT s.id, e.name_related , s.date_start, s.date_finished, \
               p.name "
        sql += "FROM mrp_production_signing s "
        sql += "INNER JOIN hr_employee e ON s.employee_id=e.id "
        sql += "INNER JOIN mrp_production p ON p.id = s.production_id "
        sql += "WHERE DATE(s.date_start)>='" + str(start_date) + "'"
        sql += "AND DATE(s.date_start)<='" + str(end_date) + "'"
        if employee:
            sql += " and e.id=" + str(employee.id) + " "
        else:
            sql += " and e.id=" + str(empl) + " "
        if order:
            sql += " and p.id=" + str(order.id) + " "
        if employee:
            sql += "ORDER BY s.date_start ,e.name_related "
        self.cr.execute(sql)
        results = self.cr.fetchall()
        att_ids = [x[0] for x in results]
        res = []
        for ord in prod.browse(self.cr, self.uid, att_ids):
            date_s = datetime.strptime(ord.date_start, '%Y-%m-%d %H:%M:%S')
            vals = {
                'employee': ord.employee_id and ord.employee_id.name or None,
                'start_date': date_s.strftime('%d-%m-%Y %H:%M:%S'),
                'start_time': date_s.time(),
                'order_prod': ord.production_id.name,
                'end_date': None,
                'end_time': None,
                'hours': 0.0}
            vals['employee'] += ' ('+ord.employee_id.internal_code+')'
            if ord.date_finished is not False:
                date_e = datetime.strptime(ord.date_finished,
                                           '%Y-%m-%d %H:%M:%S') or None
                vals['end_date'] = date_e.strftime('%d-%m-%Y %H:%M:%S') or None
                vals['end_time'] = date_e.time() or None
            if ord.date_finished is not False:
                start_date = datetime.strptime(vals['start_date'],
                                               '%d-%m-%Y %H:%M:%S')
                end_date = datetime.strptime(vals['end_date'],
                                             '%d-%m-%Y %H:%M:%S')
                diff = abs(end_date - start_date)
                total_seconds = diff.seconds + (diff.days * 24 * 60 * 60)
                hours = total_seconds / 3600.0
                vals['hours'] = hours
            res.append(vals)
        return res

    def get_total_signings(self, empl):
        prod = self.pool.get('mrp.production.signing')
        order = self.data_report and self.data_report[
            'order_id'] and prod.browse(
            self.cr, self.uid, self.data_report['order_id'][0]) or None

        start_date = self.data_report and datetime.strptime(
            self.data_report['start_date'], '%Y-%m-%d') or time
        end_date = datetime.strptime(
            self.data_report['end_date'], '%Y-%m-%d') or time
        emp_obj = self.pool.get('hr.employee')
        employee = self.data_report and self.data_report[
            'employee_id'] and emp_obj.browse(
                self.cr, self.uid, self.data_report['employee_id'][0]) or None
        sql = " SELECT s.id, e.name_related , s.date_start, s.date_finished, \
                p.name "
        sql += "FROM mrp_production_signing s "
        sql += "INNER JOIN hr_employee e ON s.employee_id='"+str(empl)+"'"
        sql += "INNER JOIN mrp_production p ON p.id = s.production_id "
        sql += "WHERE DATE(s.date_start)>='" + str(start_date) + "'"
        sql += "AND DATE(s.date_start)<='" + str(end_date) + "'"
        if employee:
            sql += " and e.id=" + str(employee.id) + " "
        else:
            sql += " and e.id=" + str(empl) + " "
        if order:
            sql += " and p.id=" + str(order.id) + " "
        if employee:
            sql += "ORDER BY s.date_start ,e.name_related "
        self.cr.execute(sql)
        results = self.cr.fetchall()
        att_ids = [x[0] for x in results]
        hours = 0.0
        for ord in prod.browse(self.cr, self.uid, att_ids):
            if ord.date_start is not False and ord.date_finished is not False:
                date_s = datetime.strptime(ord.date_start, '%Y-%m-%d %H:%M:%S')
                date_e = datetime.strptime(ord.date_finished,
                                           '%Y-%m-%d %H:%M:%S') or None
                diff = abs(date_e - date_s)
                total_seconds = diff.seconds + (diff.days * 24 * 60 * 60)
                hours += total_seconds / 3600.0
                date_s = None
        return hours


# Clase parser para el wizard
class signings_report_empl(osv.AbstractModel):
    _name = 'report.dx_order_signings_report.report_signings_employee'
    _inherit = 'report.abstract_report'
    _template = 'dx_order_signings_report.report_signings_employee'
    _wrapped_report_class = signings_report_employee
