# Copyright 2017 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class PartnerXlsx(models.AbstractModel):
    _name = "report.report_xlsx.purchase_line_xlsx"
    _inherit = "report.report_xlsx.abstract"
    _description = "Purchase Line XLSX Report"

    def get_partners(self, line_ids):
        return line_ids.filtered(lambda x: x.accept).mapped('partner_id')

    def get_total_approve_lines(self, line_ids, partner_id):
        return sum(x.price_total for x in line_ids.filtered(lambda x: x.accept and x.partner_id.id == partner_id))

    def generate_xlsx_report(self, workbook, data, records):
        sheet = workbook.add_worksheet("Report")

        heading = workbook.add_format(
            {'align': 'center', 'bold': True, 'font_size': '10px',
             'bg_color': '#c0c1c0',
             'border': 1,
             'border_color': 'black'})

        txt = workbook.add_format({'font_size': '10px', 'border': 1, 'align': 'center', })
        txt_highlight = workbook.add_format(
            {'font_size': '10px', 'border': 1, 'align': 'center', 'bg_color': '#ebeced', })
        title_style = workbook.add_format(
            {'font_size': '12px', 'border': 1, 'align': 'center', })

        row = 0
        requisition_num = records[0].unpacking_id.requisition_id.name if records else ''
        title = "كشف تفريغ عروض اسعار طلب شراء" + " " + requisition_num
        sheet.merge_range(row, 1, row, 5, title, title_style)

        row += 1
        sheet.write(row, 0, "الصنف", heading)
        sheet.write(row, 1, "المورد", heading)
        sheet.write(row, 2, "سعر الوحدة", heading)
        sheet.write(row, 3, "الكمية", heading)
        sheet.write(row, 4, "الاجمالى", heading)
        sheet.write(row, 5, "تاريخ الاستلام", heading)
        sheet.write(row, 6, "الحالة", heading)
        col = 7
        for partner in self.get_partners(records):
            sheet.write(row, col, partner.name, heading)
            col += 1
        row += 1
        for rec in records:
            status = 'تم الموافقة' if rec.accept else 'مرفوض'
            date_order = fields.Date.to_string(rec.date_order)
            style = txt_highlight if rec.product_name else txt
            sheet.write(row, 0, rec.product_name if rec.product_name else '', style)
            sheet.write(row, 1, rec.partner_id.name, style)
            sheet.write(row, 2, rec.price_unit, style)
            sheet.write(row, 3, rec.product_qty, style)
            sheet.write(row, 4, rec.price_total, style)
            sheet.write(row, 5, date_order, style)
            sheet.write(row, 6, status, style)
            col = 7
            for partner in self.get_partners(records):
                if partner == rec.partner_id and rec.accept:
                    sheet.write(row, col, rec.price_total, style)
                else:
                    sheet.write(row, col, "", style)
                col += 1
            row += 1

        # footer
        sheet.merge_range(row, 0, row, 6, "الاجمالى", heading)
        col = 7
        for partner in self.get_partners(records):
            total = self.get_total_approve_lines(records, partner.id)
            sheet.write(row, col, total, heading)
            col += 1

        sheet.set_column(0, 0, 20)
        sheet.set_column(0, 1, 15)
