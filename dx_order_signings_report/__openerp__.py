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

{
    'name': "Order Signings Report",
    'version': "1.0",
    'author': "Domatix",
    'category': 'Custom Reporting',
    'description': """
    This module define the signings order report.
    """,
    'license': "GPL-3",
    'depends': ['base', 'report'
                ],
    "update_xml": [
                   ],
    'data': [
             'report/signings_report.xml',
             'views/signing_report_view_date.xml',
             'views/signing_report_view_employee.xml',
             'wizard/order_signings_view.xml',
    ],
    'installable': True,
}