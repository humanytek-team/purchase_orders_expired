# -*- coding: utf-8 -*-
# Copyright 2017 Humanytek - Manuel Marquez <manuel@humanytek.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

{
    'name': 'Manager of Purchase Orders Expired',
    'version': '9.0.1.0.0',
    'category': 'Purchases',
    'author': 'Humanytek',
    'website': "http://www.humanytek.com",
    'license': 'AGPL-3',
    'depends': ['purchase', 'purchase_order_date_receipt_supplier'],
    'data': [
        'views/res_company_view.xml',
        'views/purchase_view.xml',
        'data/ir_cron.xml',
        'data/mail_template_data.xml',
    ],
    'installable': True,
    'auto_install': False
}
