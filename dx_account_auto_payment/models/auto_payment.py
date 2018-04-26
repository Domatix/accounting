# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2015 Domatix (http://www.domatix.com)
#                       info <email@domatix.com>
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

from odoo import models, api, fields, _

class AutoPayment(models.Model):
    _name = 'account.payment.auto'

    name = fields.Char(
        string='Name',
        default='Auto Payment')

    payment_ids = fields.Many2many(
        comodel_name='account.payment.mode',
        string='Payment mode')


    _sql_constraints = [(
        'ref_auto_payment_name_uniq',
        'unique(name)',
        'Only one auto payment record can be saved'
        )]
