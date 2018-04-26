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

from odoo import models, _,fields, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    vat_ids = fields.One2many(
        comodel_name='res.company.vats',
        inverse_name='company_id',
        string='Multiple Vat')


class CompanyVats(models.Model):
    _name = 'res.company.vats'
    _description = 'Company Vats'

    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company')

    country_id = fields.Many2one(
        comodel_name='res.country',
        string='Country')

    iso_code = fields.Char(
        string='ISO')

    tax_id = fields.Many2one(
        comodel_name='account.tax',
        string='Tax')


    vat = fields.Char(
        string='VAT')

    @api.onchange('country_id')
    def _onchange_country_name(self):
        if self.country_id:
            self.iso_code = self.country_id.code
