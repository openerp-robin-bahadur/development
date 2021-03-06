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
    'name' : 'Mudd Project',
    'version' : '1.1',
    'author' : 'Bista Solutions',
    'category' : 'Mudd Advertising',
    'description' : """

    """,
    'website': 'http://www.bistasolutions.com',
    'images' : [],
    'depends' : ['base','sale', 'product','product_custom_attributes','stock','crm','purchase'],
    'data': [
#                'wizard/brand_manager_commission_view.xml',
                'wizard/miscellaneous_view.xml',
                'wizard/sale_price_history_wizard_view.xml',
                'view/account_view.xml',
                'view/custom_attribute_view.xml',
                'view/res_partner_view.xml',
                'view/sale_view.xml',
                'view/base_product_view.xml',
                'view/mail_view.xml',
#                'view/special_commission_view.xml',
#                'view/account_view.xml',
                
    ],
    'js': [],
    'qweb' : [],
    'css':[],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
