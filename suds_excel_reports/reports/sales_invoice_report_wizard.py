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
        content_float = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter'})
        center_size = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter'})

        center_size.set_font_size(30)

        content_float.set_num_format('0.00')


        sales_invoice = workbook.add_worksheet("Sales and Invoice Summary")

        sales_invoice.set_column('A:A', 15)
        sales_invoice.set_column('B:B', 13)
        sales_invoice.set_column('C:C', 27)
        sales_invoice.set_column('D:C', 27)
        sales_invoice.set_column('E:E', 22)
        sales_invoice.set_column('F:F', 17)
        sales_invoice.set_column('G:G', 18)
        sales_invoice.set_column('H:H', 22)
        sales_invoice.set_column('I:I', 22)
        sales_invoice.set_column('J:J', 13)
        sales_invoice.set_column('K:K', 18)
        sales_invoice.set_column('L:L', 15)

        sales_invoice.merge_range('D1:G2', "SALES AND INVOICE REPORT",center_size)

        sales_invoice.write(4, 0, "Customer",border)
        sales_invoice.write(4, 1, "SO No.",border)
        sales_invoice.write(4, 2, "SO Date.",border)
        sales_invoice.write(4, 3, "Category",border)
        sales_invoice.write(4, 4, "Product",border)
        sales_invoice.write(4, 5, "SO Ordered Qty",border)
        sales_invoice.write(4, 6, "SO Total Amount",border)
        sales_invoice.write(4, 7, "Invoice No.",border)
        sales_invoice.write(4, 8, "Invoice Date",border)
        sales_invoice.write(4, 9, "Quantity",border)
        sales_invoice.write(4, 10, "Invoice Total Amount",border)
        sales_invoice.write(4, 11, "Invoice Status",border)


        row = 5

        for rec in records:
            invoice = rec.env['account.invoice'].search([
                ('state', '=', 'open'),
                ('type','=','out_invoice')])
            for inv in invoice:
                for i in inv.invoice_line_ids:
                    sales_invoice.write(row, 0, inv.partner_id.name, content)
                    sales_invoice.write(row, 1, inv.origin, content)
                    sales_invoice.write(row, 2, inv.invoice_sales_document.confirmation_date, content)
                    sales_invoice.write(row, 3, i.product_id.categ_id.name, content)
                    sales_invoice.write(row, 4, i.product_id.name, content)
                    sales_invoice.write(row, 5, i.quantity, content)
                    sales_invoice.write(row, 6, inv.invoice_sales_document.amount_total, content_float)
                    sales_invoice.write(row, 7, inv.number, content)
                    sales_invoice.write(row, 8, inv.date_invoice, content)
                    sales_invoice.write(row, 9, i.quantity, content)
                    sales_invoice.write(row, 10, inv.amount_total, content_float)
                    sales_invoice.write(row, 11, inv.state, content)
                row += 1
            row += 2
