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
from openerp import fields, models


class res_partner_email_count(models.Model):
    _inherit = 'res.partner'
    email_count = fields.Char('Financial Email',
                              help="This field is for the Financial Email "
                              "for 347 letter",
                              size=64)


class res_company_email_signature(models.Model):
    _inherit = 'res.company'
    signature = fields.Binary('Email signature',
                              help="This field is for the signature "
                              "for 347 letter",
                              store=True,)
