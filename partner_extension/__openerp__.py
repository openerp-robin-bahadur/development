# -*- coding: utf-8 -*-
{
    'name': 'Partner Extension',
    'version': '1.0',
    'category': 'Verticals',
    'sequence': 190,
    'summary': "Partner Extension, Adds custom fields for Salesforce integration in Partner model",
    'description': """
              This is useful as we integrate more application with openerp, we can use this as a common module.
       """,
    'author': 'Bista Solutions',
    'website': 'http://bistasolutions.com',
    'images': [],
    'depends': ['base'],
    'data':[
        'partner_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}

