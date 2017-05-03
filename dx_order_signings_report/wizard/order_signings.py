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
from openerp.osv import osv, fields


class order_signings(osv.TransientModel):
    _name = 'dx_order_signings_report.order_signings'
    _description = 'Print Order Signings List Report'
    _columns = {
        'start_date': fields.date('Start Date', required=True),
        'end_date': fields.date('End Date', required=True),
        'order_id': fields.many2one('mrp.production',
                                    'Select Manufactured Order'),
        'employee_id': fields.many2one('hr.employee',
                                       "Employee's Name", select=True),
        'group_by': fields.selection([('employee', 'Employee'),
                                      ('date', 'Date')],
                                     'Group by',
                                     required=True),
    }
    _defaults = {
        'start_date': lambda *a: time.strftime('%Y-%m-01'),
        'end_date': lambda *a: time.strftime('%Y-%m-%d'),
        'group_by': 'employee',
    }

    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        data = self.read(cr, uid, ids)[0]
        context['data_report'] = data

        report = 'dx_order_signings_report.report_signings_'+data['group_by']
        datas = {
             'ids': [],
             'model': 'hr.employee',
             'form': data,
             'context': context,
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': report,
            'datas': datas,
            'context': context,
        }


order_signings()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
