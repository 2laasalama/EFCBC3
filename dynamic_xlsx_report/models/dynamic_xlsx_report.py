# -*- coding: utf-8 -*-
from odoo import models


class PartnerXlsx(models.AbstractModel):
    _name = "report.report_xlsx.dynamic_xlsx_report"
    _inherit = "report.report_xlsx.abstract"

    def get_field_value(self, obj, field):
        value = obj[field.name]
        if field.ttype == 'many2one':
            value = value.name_get()[0][1]
            return value
        else:
            return value

    def generate_xlsx_report(self, workbook, data, records):
        template_id = data['template_id']
        if not template_id:
            return

        template = self.env['report.template'].browse(int(template_id))
        mapping_lines = self.env['template.mapping.line'].search([('template_id', '=', int(template_id))],
                                                                 order='sequence')
        sheet = workbook.add_worksheet("Report")
        bold = workbook.add_format({"bold": True})

        row, col = 0, 0
        # table header
        sheet.write(row, col, '#', bold)
        for line in mapping_lines:
            col += 1
            sheet.write(row, col, line.label, bold)

        # table body
        for rec in records:
            col = 0
            row += 1
            sheet.write(row, col, row)
            for line in mapping_lines:
                col += 1
                field_value = self.get_field_value(rec, line.field_id)
                sheet.write(row, col, field_value)
