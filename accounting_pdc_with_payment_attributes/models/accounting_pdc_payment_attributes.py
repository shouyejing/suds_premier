from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.safe_eval import safe_eval
from datetime import date, datetime, timedelta
import logging
_logger = logging.getLogger(__name__)


class PDCPaymentAttributeAccountJournal(models.Model):
    _inherit = "account.journal"

    @api.one
    @api.depends('outbound_payment_method_ids')
    def _compute_check_printing_payment_method_selected(self):
        self.check_printing_payment_method_selected = any(
            pm.code in ['check_printing', 'pdc'] for pm in self.outbound_payment_method_ids)

    @api.model
    def _enable_pdc_on_bank_journals(self):
        """ Enables check printing payment method and add a check sequence on bank journals.
            Called upon module installation via data file.
        """
        pdcin = self.env.ref('account_pdc.account_payment_method_pdc_in')
        pdcout = self.env.ref('account_pdc.account_payment_method_pdc_out')
        bank_journals = self.search([('type', '=', 'bank')])
        for bank_journal in bank_journals:
            # bank_journal._create_check_sequence()
            bank_journal.write({
                'inbound_payment_method_ids': [(4, pdcin.id, None)],
                'outbound_payment_method_ids': [(4, pdcout.id, None)],
            })


class PDCPaymentAttributeAccountPayment(models.Model):
    _inherit = 'account.payment'

    bank_reference = fields.Char(string="Bank Reference")
    cheque_reference = fields.Char(string="Cheque Reference")
    effective_date = fields.Date('Effective Date', help='Effective date of PDC')

    @api.multi
    def print_checks(self):
        """ Copy-pasted override from the original account.payment model. Changes all have 'PDC' """
        """ Check that the recordset is valid, set the payments state to sent and call print_checks() """
        # Since this method can be called via a client_action_multi, we need to make sure the received records are what we expect
        self = self.filtered(lambda r: r.payment_method_id.code in ['check_printing', 'pdc'] and r.state != 'reconciled')

        if len(self) == 0:
            raise UserError(_("Payments to print as a checks must have 'Check' or 'PDC' selected as payment method and "
                              "not have already been reconciled"))
        if any(payment.journal_id != self[0].journal_id for payment in self):
            raise UserError(_("In order to print multiple checks at once, they must belong to the same bank journal."))

        if not self[0].journal_id.check_manual_sequencing:
            # The wizard asks for the number printed on the first pre-printed check
            # so payments are attributed the number of the check the'll be printed on.
            last_printed_check = self.search([
                ('journal_id', '=', self[0].journal_id.id),
                ('check_number', '!=', 0)], order="check_number desc", limit=1)
            next_check_number = last_printed_check and last_printed_check.check_number + 1 or 1
            return {
                'name': _('Print Pre-numbered Checks'),
                'type': 'ir.actions.act_window',
                'res_model': 'print.prenumbered.checks',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'payment_ids': self.ids,
                    'default_next_check_number': next_check_number,
                }
            }
        else:
            self.filtered(lambda r: r.state == 'draft').post()
            self.write({'state': 'sent'})
            return self.do_print_checks()

    @api.multi
    def _get_move_vals(self, journal=None):
        res = super(PDCPaymentAttributeAccountPayment, self)._get_move_vals()
        res.update({'bank_reference':self.bank_reference,
                    'cheque_reference':self.cheque_reference,
                    'effective_date':self.effective_date,
                    })
        if self.payment_method_code =='pdc':
            res['date'] = self.effective_date
        else:
            res['date'] = self.payment_date
        return res

class PDCPaymentAttributeAccountMove(models.Model):
    _inherit = 'account.move'

    bank_reference = fields.Char(string="Bank Reference")
    cheque_reference = fields.Char(string="Cheque Reference")
    effective_date = fields.Date('Effective Date(PDC Only)', help='Effective date of PDC')
