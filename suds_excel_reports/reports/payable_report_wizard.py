from odoo import fields, models
import logging

_logger = logging.getLogger(__name__)


class PayableReportWizard(models.TransientModel):
    _name = "payable.report"

    msg = fields.Char(default="PAYABLE REPORT")

    date_from = fields.Date("Start Date")
    date_to = fields.Date("End Date")


class payablexlsxreport(models.AbstractModel):
    _name = 'report.report_rl.payablexlsxreport'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, records):

        border = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'bold': True})
        content = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter'})
        content_float = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter'})
        center_size = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter'})

        center_size.set_font_size(30)

        content_float.set_num_format('0.00')


        payable = workbook.add_worksheet("Payable Summary")

        payable.set_column('A:A', 13)
        payable.set_column('B:B', 23)
        payable.set_column('C:C', 27)
        payable.set_column('D:D', 24)
        payable.set_column('E:E', 23)
        payable.set_column('F:F', 20)
        payable.set_column('G:G', 15)


        payable.merge_range('B1:F2', "Payable Report", center_size)

        payable.write(4, 0, "PO No.",border)
        payable.write(4, 1, "PO Date.",border)
        payable.write(4, 2, "Invoice No.",border)
        payable.write(4, 3, "Invoice Date",border)
        payable.write(4, 4, "Total Amount",border)
        payable.write(4, 5, "Total Amount Due",border)
        payable.write(4, 6, "Invoice Status",border)

        row = 5

        for rec in records:
            vendor = rec.env['account.invoice'].search([
                ('state', 'in', ('paid','open')),
                ('type','=','in_invoice')])
            for po in vendor:
                if (po.date_invoice >= rec.date_from and
                    po.date_invoice <= rec.date_to):
                    purchase_order = rec.env['purchase.order'].search([
                        ('name', '=', po.origin)])
                    payable.write(row, 0, po.origin, content)
                    payable.write(row, 1, purchase_order.date_order, content)
                    payable.write(row, 2, po.number, content)
                    payable.write(row, 3, po.date_invoice, content)
                    payable.write(row, 4, po.amount_total, content_float)
                    payable.write(row, 5, po.residual, content_float)
                    payable.write(row, 6, po.state, content)
                    row += 1
