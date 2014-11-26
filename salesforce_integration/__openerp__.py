{
    'name': 'SalesForce',
    'version': '1.0',
    'category': 'tools',
    "sequence": 150,
    'summary': "SalesForce Integraton",
    'description': """
SalesForce Integration
======================
This module synchronise SalesForce and OpenERP \n
It can be used to import and export data from openerp to SalesForce,
Following objects can be synced\n
Partner\n,Contacts\n. 
    """,

    'author': 'Bista Solutions',
    'website': 'http://bistasolutions.com',
    'depends': ['base','partner_extension','bista_product_attribute','logger','warning_popup','account_analytic_analysis'],
    'data': [
        'security/salesforce_security.xml',
        'salesforce_view.xml',
        'salesforce_reference_view.xml',
        'lead_view.xml',
        'security/ir.model.access.csv',
    ],
    'init_xml': [
            'data/salesforce.tables.csv',
#             'data/salesforce.fields.csv'
                ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
