# -*- coding: utf-8 -*-
# Copyright 2017 Domatix - Juan Cuesta Contreras
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': "Registro de iva",
    'version': "10.0.1.0.1",
    'author': "Domatix",
    'category': 'Custom Reporting',
    'description': """
    This module prints a custom report for IVA register
    """,
    "website": "http://www.domatix.com/",
    'license': "GPL-3",
    'depends': ['base', 'report', 'account'],
    "update_xml": [
                   ],
    'data': ['wizard/iva_record.xml',
             'report/iva_record_report.xml',
             ],
    'installable': True,
}
