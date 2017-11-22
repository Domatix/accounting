# -*- coding: utf-8 -*-
###############################################################################
#    Module created by domatix
#    Odoo, Open Source Management Solution
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
from odoo import models, fields
from itertools import groupby


class iva_record_wizzard(models.TransientModel):
    _name = 'dx_iva_record.iva_record_wizard'

    def get_data(self):
        if self.partner_type == 'supplier':
            invoice_tax_obj = self.env['account.invoice.tax'].search([('invoice_id.date', '>=', self.date_start), ('invoice_id.date', '<=', self.date_end), ('tax_code_id.id', 'in', self.tax_ids.ids), ('company_id', '=', self.company_id.id), ('invoice_id.state', 'in', ['open', 'paid']), ('invoice_id.type', 'in', ['in_invoice', 'in_refund'])])
        elif self.partner_type == 'client':
            invoice_tax_obj = self.env['account.invoice.tax'].search([('invoice_id.date', '>=', self.date_start), ('invoice_id.date', '<=', self.date_end), ('tax_code_id.id', 'in', self.tax_ids.ids), ('company_id', '=', self.company_id.id), ('invoice_id.state', 'in', ['open', 'paid']), ('invoice_id.type', 'in', ['out_invoice', 'out_refund'])])
        else:
            invoice_tax_obj = self.env['account.invoice.tax'].search([('invoice_id.date', '>=', self.date_start), ('tax_code_id.id', 'in', self.tax_ids.ids), ('invoice_id.date', '<=', self.date_end)])
        positive = invoice_tax_obj.filtered(lambda r: r.invoice_id.amount_untaxed_signed > 0 and 'igic' not in r.name)
        negative = invoice_tax_obj.filtered(lambda r: r.invoice_id.amount_untaxed_signed < 0 and 'igic' not in r.name)

        res_dict = {}
        positive = sorted(positive, key=lambda x: x.invoice_id.move_id.date)
        negative = sorted(negative, key=lambda x: x.invoice_id.move_id.date)
        res_dict['positive'] = {}
        res_dict['negative'] = {}

        for key, group in groupby(positive, lambda x: x.name):
            if key not in res_dict['positive']:
                res_dict['positive'][key] = []
            for tax in group:
                res_dict['positive'][key].append(tax)
        for key, group in groupby(negative, lambda x: x.name):
            if key not in res_dict['negative']:
                res_dict['negative'][key] = []
            for tax in group:
                res_dict['negative'][key].append(tax)
        if self.igic:
            igic_negative = invoice_tax_obj.filtered(lambda r: r.invoice_id.amount_untaxed_signed < 0 and 'igic' in r.name)
            igic_positive = invoice_tax_obj.filtered(lambda r: r.invoice_id.amount_untaxed_signed > 0 and 'igic' in r.name)
            igic_positive = sorted(igic_positive, key=lambda x: x.invoice_id.move_id.date)
            igic_negative = sorted(igic_negative, key=lambda x: x.invoice_id.move_id.date)
            res_dict['igic_positive'] = {}
            res_dict['igic_negative'] = {}
            for key, group in groupby(igic_positive, lambda x: x.name):
                if key not in res_dict['igic_positive']:
                    res_dict['igic_positive'][key] = []
                for tax in group:
                    res_dict['igic_positive'][key].append(tax)
            for key, group in groupby(igic_negative, lambda x: x.name):
                if key not in res_dict['igic_negative']:
                    res_dict['igic_negative'][key] = []
                for tax in group:
                    res_dict['igic_negative'][key].append(tax)
        return res_dict.items()

    company_id = fields.Many2one('res.company', 'Company',
                                 help='Company',
                                 required=True,
                                 default=lambda self: self.env.user.company_id)
    date_start = fields.Date(
        string='Start date')
    date_end = fields.Date(
        string='End date')

    display_zero = fields.Boolean('Display Zero acc')

    partner_ids = fields.Many2many(comodel_name='res.partner',
                                   string='Partner',
                                   help='Déjelo vacío para todas las empresas')
    tax_ids = fields.Many2many(comodel_name='account.code.tax', string='Taxes')

    partner_type = fields.Selection(
        [('client', 'Cliente'), ('supplier', 'Proveedor')],
        string='Tipo de factura',
        help='Déjelo vacío para todos los tipos de factura')
    igic = fields.Boolean(string="¿Incluir IGIC?")

    def print_report(self, ids, context=None):

        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'dx_iva_record.report_iva_record'
        }
