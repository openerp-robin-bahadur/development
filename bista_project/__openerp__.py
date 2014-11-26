# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Project Management',
    'version': '1.1',
    'author': 'Bista Solutions',
    'website': 'http://www.openerp.com',
    'category': 'Project Management',
    'sequence': 9,
    'summary': 'Projects, Tasks',
    'images': [],
    'depends': [
        'base_setup',
        'base_status',
        'product',
        'analytic',
        'project',
        'sale',
        'quoteflow',
        'project_long_term',
        
    ],
    'description': """
Track team of Parent Project
=====================================================

    """,
    'data': ['wizard/project_template_view.xml',
             'wizard/compute_task_view.xml',
             'project_code_sequence.xml',
             'project_view.xml',
#             'sale_view.xml'
             ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'css': [],
    'js': [],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
