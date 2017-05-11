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
from openerp import models, api, _
from datetime import datetime
import openerp
import base64


class report_347(models.Model):
    _inherit = "l10n.es.aeat.mod347.report"

    @api.multi
    def btn_list_records(self):
        return {
            'domain': "[('report_id','in'," + str(self.ids) + ")]",
            'name': _("Partner records"),
            'view_mode': 'tree,form',
            'view_type': 'form',
            'res_model': 'l10n.es.aeat.mod347.partner_record',
            'type': 'ir.actions.act_window',
        }

    def get_date(self):
        company = self.company_id.city
        res = company + ",   "
        date = datetime.today()
        day = date.strftime("%d")
        month = date.strftime("%B").upper()
        year = date.strftime("%Y")
        res += day + _("  of  ")
        res += month + _("  of  ")
        res += year
        return res

    def calculate(self):
        res = super(report_347, self).calculate()
        if res:
            partner_records = self.partner_record_ids
            for record in partner_records:
                conditions = [('report_type', 'in', ['qweb-pdf', 'qweb-html']),
                              ('report_name', '=',
                               u'dx_347_letter.report_347_letter')]
                report = self.env['ir.actions.report.xml'].search(conditions)[
                    0]
                result, format = openerp.report.render_report(
                    record._cr,
                    record._uid,
                    [record.id],
                    report.report_name,
                    {'model': record._name},
                    context=record._context)

                result = base64.b64encode(result)
                file_name = "Carta_347.pdf"
                repeated_doc_cond = [('name', '=', file_name),
                                     ('partner_id', '=', record.partner_id.id),
                                     ('company_id', '=',
                                      record.report_id.company_id.id)]
                repeated_docs = self.env[
                    'ir.attachment'].search(repeated_doc_cond)
                if repeated_docs:
                    repeated_docs.unlink()
                self.env['ir.attachment'].create(
                    {'name': file_name,
                     'datas': result,
                     'datas_fname': file_name,
                     'res_model': 'res.partner',
                     'type': 'binary',
                     'partner_id': record.partner_id.id,
                     'company_id': record.report_id.company_id.id
                     })

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
