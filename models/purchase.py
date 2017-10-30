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
                    orders_expired.write({'state': 'expired'})
                    _logger.info('Purchase orders expired were found')
                    for po in orders_expired:
                        _logger.info('Purchase expired %s', po.name)
