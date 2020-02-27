# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime, timedelta
import logging
import itertools
import calendar
from odoo.exceptions import ValidationError
from num2words import num2words
_logger = logging.getLogger("_name_")


class SalesReportXlsx(models.AbstractModel):
    _name = 'report.sales_history_report'
    _inherit = 'report.report_xlsx.abstract'

    # transaction = fields.Selection(
    #     string='Transaction',
    #     selection=[('purchase', 'Purchases'),
    #                ('sale', 'Sales')]
    # )
    # from_date = fields.Date(string="Start Date")
    # to_date = fields.Date(string="End Date")

    def generate_xlsx_report(self, workbook, data, line, *args, **kwargs):

        # FETCHING DATA FROM DATABASE
        a = []
        for i in line:
            a.append(i.id)
        selected_invoice_line_records = self.env['account.invoice.line'].search(
            [('invoice_id', 'in', a), ('invoice_id.state', 'in', ['draft','open', 'paid'])])  # Gets all invoice line records where id is in list "a"
        selected_invoice_records = self.env['account.invoice'].search(
            [('id', 'in', a), ('state', 'in', ['draft','open', 'paid'])])  # Gets all invoice records where id is in list "a" and state is either 'open' and 'paid'
        _logger.info(
            '\n\n\nSelected Records {} \n\n\n'.format(selected_invoice_line_records))
        _logger.info("\n\n\nSelf {}\nWorkbook {}Data {}\nLine {}\n\n\n".format(
            self, workbook, data, line))
        
        # months = sorted(
        #     list(i.invoice_id.date_invoice for i in selected_invoice_line_records))
        months=list()
        for i in selected_invoice_line_records:
            if i.invoice_id.date_invoice:
                months.append(i.invoice_id.date_invoice)

        month_range = list(datetime.strptime(x, '%Y-%m-%d') for x in sorted(months))
        _logger.info(
            '\n\n\nMonths {}\nMonths Mapped {}\nMonth Range {}\n\n\n'.format(
                months,
                list(map(lambda x: datetime.strptime(x, '%Y-%m-%d'), months)),
                month_range
                # [datetime.strptime(x,'%Y-%m-%d') for x in months]
                # [lambda x: datetime.strptime(x,'%Y-%m-%d') for x in months],
            ))

        # TOP COLUMN HEADERS
        top_column = ["Customer", "Invoice Sales Document",
                      "Invoice Date", "Due Date", "Salesperson", "Product",
                      "Product Category", "Account", "Analytic Account",
                      "Quantity", "Cost Price", "Unit Price","Subtotal","Status"]
        sheet = workbook.add_worksheet(
            "Sales Report {}".format(datetime.now().strftime('%m-%d-%Y')))
        title = 'SUDS PREMIERE FRANCHISING CORPORATION\nSALES REPORT {} {}'.format(
            'FOR ' + month_range[0].strftime('%b %Y').upper()
            if len(month_range) != 0 and month_range[0] else "",
            'TO ' + month_range[-1].strftime('%b %Y').upper() if (len(month_range) != 0)
            and (month_range[-1].strftime('%b %Y') != month_range[0].strftime('%b %Y')) else "")
        _logger.info('\n\n\nTITLE:{}\n\n\n'.format(title))

    # ============ALL CELL FORMATTING GOES HERE============

        # TITLE
        title_format = workbook.add_format({
            'font_name': 'Arial',
            'font_size': 13,
            'valign': 'vcenter',
            'align': 'left',
            'bold': True,
            'font_color': 'red',
            # 'text_wrap': True
        })

        # HEADER
        header_format = workbook.add_format({
            'font_name': 'Arial',
            'font_size': 10,
            'valign': 'vcenter',
            'align': 'center',
            'bold': True,
        })

        # DATA
        data_format = workbook.add_format({
            'font_size': 10,
            'valign': 'vcenter',
            'align': 'center',
            # 'num_format': '[$Php-3409]#,##0.00;-[$Php-3409]#,##0.00',
            # 'text_wrap': True
        })

        # TOTALS
        total_amount_format = workbook.add_format({
            'font_size': 13,
            'valign': 'vcenter',
            'align': 'center',
            'num_format': '[$Php-3409]#,##0.00;-[$Php-3409]#,##0.00',
            'bold': True,
            'font_color': 'red',
            # 'bottom': 6,
            # 'top': 1,
        })

        total_sales_format = workbook.add_format({
            'font_size': 13,
            'valign': 'vcenter',
            'align': 'center',
            'num_format': '[$Php-3409]#,##0.00;-[$Php-3409]#,##0.00',
            'bold': True,
            # 'bottom': 6,
            # 'top': 1,
        })

    # ===================================================================================================================

    # =====================================ALL CELL PRINTING GOES HERE===================================================

        column_length = len(top_column)
        sheet.merge_range(0, 0, 1, (column_length-1), title, title_format)
        sheet.write_row(4, 0, top_column, header_format)
        sheet.set_column('C:C', 20, header_format,
                         #  {'hidden': 1}
                         )
        sheet.set_row(4, 30)

        counter = 5
        amount_untaxed = []
        amount_tax = []
        amount_total = []
        amount_due = []
        if selected_invoice_line_records[:1]:
            for i in selected_invoice_line_records:
                state = dict(i.invoice_id._fields['state'].selection).get(i.invoice_id.state)
                data_columns = [
                    i.invoice_id.partner_id.name.upper(),  # CUSTOMER
                    i.invoice_id.invoice_sales_document.name or "None",  # INVOICE SALES DOCUMENT
                    i.invoice_id.date_invoice or "None",  # INVOICE DATE
                    i.invoice_id.date_due or "None",  # DUE DATE
                    i.invoice_id.partner_id.user_id.name or "N/A",  # SALESPERSON
                    i.product_id.name_get()[0][1] if i.product_id.name_get(
                    ) == True else i.name,  # PRODUCT OR DESCRIPTION
                    i.product_id.categ_id.name,  # PRODUCT CATEGORY
                    i.account_id.name_get()[0][1],  # ACCOUNT
                    i.account_analytic_id.name or "N/A",  # ANALYTIC ACCOUNT
                    i.quantity,  # QUANTITY
                    i.product_id.standard_price,  # COST PRICE
                    i.price_unit,  # UNIT PRICE
                    i.price_subtotal,  # SUB TOTAL
                    state, #STATUS
                ]
                sheet.write_row((counter+1), 0, data_columns, data_format)
                if i.invoice_id.amount_untaxed not in amount_untaxed:
                    amount_untaxed.append(i.invoice_id.amount_untaxed)
                if i.invoice_id.amount_tax not in amount_tax:
                    amount_tax.append(i.invoice_id.amount_tax)
                if i.invoice_id.amount_total not in amount_total:
                    amount_total.append(i.invoice_id.amount_total)
                if i.invoice_id.residual not in amount_due:
                    amount_due.append(i.invoice_id.residual)
                counter += 1
            _logger.info("\n\n\nAmount Untaxed{}\nAmount Tax{}\nAmount Total{}\nAmount Due{}\n\n\n\n".format(
                amount_untaxed, amount_tax, amount_total, amount_due))
    # # =====================================CELL FORMULAS FOR TAX TYPE "Y"============================================

        if selected_invoice_line_records[:1]:
            # AMOUNT UNTAXED
            sheet.write(
                counter+2, 12, "AMOUNT UNTAXED", total_amount_format)
            sheet.write(
                counter+2, 13, sum(amount_untaxed), total_amount_format)
            # AMOUNT TAX
            sheet.write(
                counter+4, 12, "TAX", total_amount_format)
            sheet.write(
                counter+4, 13, sum(amount_tax), total_sales_format)
            # AMOUNT TOTAL
            sheet.write(
                counter+6, 12, "TOTAL AMOUNT", total_amount_format)
            sheet.write(
                counter+6, 13, sum(amount_total), total_sales_format)
            # AMOUNT DUE
            sheet.write(
                counter+8, 12, "AMOUNT DUE", total_amount_format)
            sheet.write(
                counter+8, 13, sum(amount_due), total_sales_format)
