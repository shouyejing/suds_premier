from odoo import fields, models
import logging

_logger = logging.getLogger(__name__)


class SalesInvoiceReportWizard(models.TransientModel):
    _name = "sales.invoice.report"

    msg = fields.Char(default="SALES AND INVOICE REPORT")

    date_from = fields.Date("Start Date")
    date_to = fields.Date("End Date")


class salesandinvoicexlsxreport(models.AbstractModel):
    _name = 'report.report_rl.salesandinvoicexlsxreport'
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
        bold = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'bold': True})
        left = workbook.add_format({
            'align': 'left',
            'border': 1})

        bold.set_num_format('0.00')


        sales_invoice = workbook.add_worksheet("Sales and Invoice Summary")

        sales_invoice.set_column('A:A', 13)
        sales_invoice.set_column('B:B', 27)
        sales_invoice.set_column('C:C', 27)
        sales_invoice.set_column('D:D', 22)
        sales_invoice.set_column('E:E', 17)
        sales_invoice.set_column('F:F', 18)
        sales_invoice.set_column('G:G', 22)
        sales_invoice.set_column('H:H', 22)
        sales_invoice.set_column('I:I', 13)
        sales_invoice.set_column('J:J', 18)
        sales_invoice.set_column('K:K', 15)

        sales_invoice.merge_range('D1:G2', "SALES AND INVOICE REPORT",left)

        sales_invoice.write(4, 0, "SO No.",border)
        sales_invoice.write(4, 1, "SO Date.",border)
        sales_invoice.write(4, 2, "Category",border)
        sales_invoice.write(4, 3, "Product",border)
        sales_invoice.write(4, 4, "SO Ordered Qty",border)
        sales_invoice.write(4, 5, "SO Total Amount",border)
        sales_invoice.write(4, 6, "Invoice No.",border)
        sales_invoice.write(4, 7, "Invoice Date",border)
        sales_invoice.write(4, 8, "Quantity",border)
        sales_invoice.write(4, 9, "Invoice Total Amount",border)
        sales_invoice.write(4, 10, "Invoice Status",border)


        row = 5

        for rec in records:
            invoice = rec.env['account.invoice'].search([
                ('state', 'in', ('paid','open')),
                ('type','=','out_invoice')])
            for inv in invoice:
                for i in inv.invoice_line_ids:
                    sales_invoice.write(row, 0, inv.origin, content)
                    sales_invoice.write(row, 1, inv.invoice_sales_document.confirmation_date, content)
                    sales_invoice.write(row, 2, i.product_id.categ_id.name, content)
                    sales_invoice.write(row, 3, i.product_id.name, content)
                    sales_invoice.write(row, 4, i.quantity, content)
                    sales_invoice.write(row, 5, inv.invoice_sales_document.amount_total, content)
                    sales_invoice.write(row, 6, inv.number, content)
                    sales_invoice.write(row, 7, inv.date_invoice, content)
                    sales_invoice.write(row, 8, i.quantity, content)
                    sales_invoice.write(row, 9, inv.amount_total, content)
                    sales_invoice.write(row, 10, inv.state, content)
                row += 1
            row += 2
