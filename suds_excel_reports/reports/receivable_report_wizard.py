from odoo import fields, models
import logging

_logger = logging.getLogger(__name__)


class ReceivableReportWizard(models.TransientModel):
    _name = "receivable.report"

    msg = fields.Char(default="RECEIVABLE REPORT")

    date_from = fields.Date("Start Date")
    date_to = fields.Date("End Date")


class receivablexlsxreport(models.AbstractModel):
    _name = 'report.report_rl.receivablexlsxreport'
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


        receivable = workbook.add_worksheet("Receivable Summary")

        receivable.set_column('A:A', 17)
        receivable.set_column('B:B', 13)
        receivable.set_column('C:C', 23)
        receivable.set_column('D:D', 27)
        receivable.set_column('E:E', 24)
        receivable.set_column('F:F', 23)
        receivable.set_column('G:G', 20)
        receivable.set_column('H:H', 15)

        receivable.merge_range('B1:F2', "Receivable Report",center_size)

        receivable.write(4, 0, "Customer",border)
        receivable.write(4, 1, "SO No.",border)
        receivable.write(4, 2, "SO Date.",border)
        receivable.write(4, 3, "Invoice No.",border)
        receivable.write(4, 4, "Invoice Date",border)
        receivable.write(4, 5, "Total Amount",border)
        receivable.write(4, 6, "Total Amount Due",border)
        receivable.write(4, 7, "Invoice Status",border)

        row = 5

        for rec in records:
            customer_invoice = rec.env['account.invoice'].search([
                ('state', '=', 'open'),
                ('type','=','out_invoice')])
            for inv in customer_invoice:
                if (inv.date_invoice >= rec.date_from and
                    inv.date_invoice <= rec.date_to):
                    receivable.write(row, 0, inv.partner_id.name, content)
                    receivable.write(row, 1, inv.invoice_sales_document.name, content)
                    receivable.write(row, 2, inv.invoice_sales_document.confirmation_date, content)
                    receivable.write(row, 3, inv.number, content)
                    receivable.write(row, 4, inv.date_invoice, content)
                    receivable.write(row, 5, inv.amount_total, content_float)
                    receivable.write(row, 6, inv.residual, content_float)
                    receivable.write(row, 7, 'Open', content)
                    row += 1
