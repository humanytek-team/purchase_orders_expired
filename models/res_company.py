# -*- coding: utf-8 -*-
# Copyright 2017 Humanytek - Manuel Marquez <manuel@humanytek.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import fields, models


class Company(models.Model):
    _inherit = 'res.company'

    purchase_order_expiration_limit = fields.Integer(
        string=u'Limit of days to the expiration of purchase orders',
        default=30)
    fine_purchase_order_expired = fields.Float(
        string=u'Percentage of fine over purchase orders expired',
        default=5)
