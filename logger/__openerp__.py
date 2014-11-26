# -*- coding: utf-8 -*-
{
    'name': 'Logger',
    'version': '1.0',
    'category': 'tools',
    'sequence': 160,
    'summary': "Common Logger which can be used by all the integrations",
    'description': """
              This is module develoeped to register server action logs. This is a common module which all the integrations will use to register error logs . This will be useful as the user can see all the logs on a single section , even if they integrate with multiple applications.
              .
       """,
    'author': 'Bista Solutions',
    'website': 'http://bistasolutions.com',
    'images': [],
    'data': [
        'log.xml',

        ],
    'depends': ['base'],
    'installable': True,
    'auto_install': False,
    'application': True,
}

