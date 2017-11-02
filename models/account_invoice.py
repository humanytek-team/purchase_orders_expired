# -*- coding: utf-8 -*-
# Copyright 2017 Humanytek - Manuel Marquez <manuel@humanytek.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import api, models, _
from openerp.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def invoice_validate(self):
        validate_result = super(AccountInvoice, self).invoice_validate()

        if validate_result:
            AccountInvoiceLine = self.env['account.invoice.line']
            for invoice in self:

                if invoice and invoice.type == 'in_invoice':
                    purchase_orders = invoice.mapped(
                        'invoice_line_ids.purchase_id')

                    for po in purchase_orders:

                        if po.state == 'expired':
                            po_invoice_lines = invoice.invoice_line_ids.filtered(
                                lambda line: line.purchase_id and
                                line.purchase_id.id == po.id
                            )
                            po_invoice_total = 0

                            for line in po_invoice_lines:
                                po_invoice_total += line.price_subtotal

                                for tax in line.invoice_line_tax_ids:
                                    po_invoice_total += (
                                        line.price_subtotal * tax.amount) / 100

                            if po_invoice_total > 0:

                                percentage_fine = \
                                    invoice.company_id.fine_purchase_order_expired

                                if percentage_fine > 0:

                                    fine_purchase_order_expired = (
                                        po_invoice_total * percentage_fine) / 100

                                    fine_product = self.env.ref(
                                        'purchase_orders_expired.product_fine_purchase_order_expired')

                                    if fine_product:

                                        in_refund_invoice = self.create({
                                            'type': 'in_refund',
                                            'origin': invoice.number,
                                            'partner_id': invoice.partner_id.id,
                                            'currency_id': invoice.currency_id.id,
                                            'company_id': invoice.company_id.id,
                                            'user_id': invoice.user_id.id,
                                            'name': _('Fine over invoice of purchase order expired %s' % po.name)
                                            })

                                        AccountInvoiceLine.create({
                                            'invoice_id': in_refund_invoice.id,
                                            'product_id': fine_product.id,
                                            'name': fine_product.description_purchase,
                                            'quantity': 1,
                                            'price_unit': fine_purchase_order_expired,
                                            'partner_id': in_refund_invoice.partner_id.id,
                                            'account_id': \
                                                fine_product.property_account_expense_id.id,
                                            })

                                        in_refund_invoice.signal_workflow(
                                        'invoice_open')

                                    else:
                                        raise ValidationError(
                                            _('The product "Fine over purchase orders expired" has been deleted.'))

        return validate_result
