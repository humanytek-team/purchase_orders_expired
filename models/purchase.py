# -*- coding: utf-8 -*-
# Copyright 2017 Humanytek - Manuel Marquez <manuel@humanytek.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from datetime import datetime, timedelta
import logging

from openerp import api, fields, models
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    state = fields.Selection([
        ('draft', 'Draft PO'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
        ('expired', _('Expired')),
        ],
        string='Status',
        readonly=True,
        index=True,
        copy=False,
        default='draft',
        track_visibility='onchange')

    @api.multi
    def search_orders_expired(self):
        """Search for orders confirmed that are expired and change its state
        to expired"""

        today = datetime.today()
        companies = self.env['res.company'].search([])

        for company in companies:

            po_expiration_limit = company.purchase_order_expiration_limit

            if po_expiration_limit > 0:

                expiration_datetime = today - \
                    timedelta(days=po_expiration_limit)
                expiration_datetime = expiration_datetime.strftime(
                    '%Y-%m-%d %H:%M:%S')

                orders_expired = self.search([
                    ('state', '=', 'purchase'),
                    ('date_received_by_supplier', '<=', expiration_datetime),
                    ])

                if orders_expired:

                    for po in orders_expired:
                        
                        if po.invoice_ids:
                            for inv in po.invoice_ids:
                                if inv.state in ['open', 'paid']:
                                    orders_expired -= po

                        if po.picking_ids:
                            for picking in po.picking_ids:
                                if picking.state == 'done':
                                    orders_expired -= po

                if orders_expired:
                    orders_expired.write({'state': 'expired'})
                    _logger.info(
                        'Purchase orders expired were found for company %s',
                        company.name)

                    for po in orders_expired:
                        _logger.info('Purchase expired %s', po.name)

    @api.multi
    def action_rfq_send(self):
        '''
        This function opens a window to compose an email, with the edi purchase template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']

        try:
            if self.env.context.get('send_rfq', False):
                template_id = ir_model_data.get_object_reference('purchase', 'email_template_edi_purchase')[1]
            else:
                template_id = ir_model_data.get_object_reference('purchase', 'email_template_edi_purchase_done')[1]
                if self.env.context.get('send_cancelled', False):
                    template_id = ir_model_data.get_object_reference('purchase_orders_expired', 'email_template_edi_purchase_cancelled')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict(self.env.context or {})
        ctx.update({
            'default_model': 'purchase.order',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
        })
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }
