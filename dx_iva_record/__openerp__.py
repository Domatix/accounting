# encoding: utf-8
##############################################################################
#    Module created by domatix
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
    'name': "Registro de iva",
    'version': "1.0",
    'author': "Domatix",
    'category': 'Custom Reporting',
    'description': """
    This module prints a custom report for IVA register
    """,
    "website": "http://www.domatix.com/",
    'license': "GPL-3",
    'depends': ['base', 'report', 'account'
                ],
    "update_xml": [
                   ],
    'data': ['wizard/iva_record.xml',
             'report/iva_record_report.xml',
             ],
    'installable': False,
}
