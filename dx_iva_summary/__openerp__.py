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

{
    'name': "Resumen de liquidación del iva",
    'version': "1.0",
    'author': "Domatix",
    'category': 'Custom Reporting',
    'description': """
    This modeule print a custom summary report for IVA
    """,
    'license': "GPL-3",
    'depends': ['base', 'report', 'account'
                ],
    "update_xml": [
                   ],
    'data': ['wizard/iva_summary.xml',
             'report/iva_summary_report.xml',
             ],
    'installable': True,
}
