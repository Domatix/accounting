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
    'name': "347 letter",
    'version': "1.0",
    'author': "Domatix",
    'category': 'Custom Reporting',
    'description': """
    This module define the 347 report letter.
    """,
    'license': "GPL-3",
    'depends': ['l10n_es_aeat_mod347',
                'base',
                ],
    "update_xml": [
    ],
    'data': [
        'views/partner_email_acount.xml',
        'data/papelformat.xml',
        'data/email_letter_template.xml',
        'report/reports.xml',
        'views/347_letter_onedoc.xml',
        'views/347_letter_single.xml',

    ],
    'installable': True,
}
