# -*- coding: utf-8 -*-
##############################################################################
#
#    Tech Receptives, Open Source For Ideas
#    Copyright (C) 2009-TODAY Tech-Receptives Solutions Pvt. Ltd.
#                            (<http://www.techreceptives.com>)
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
from osv import osv
from osv import fields

class product_product(osv.osv):
    
    _inherit = 'product.product'
   

    _columns = {
             'LastModifiedDate':fields.datetime('LastModifiedDate'),
             'CreatedDate':fields.datetime('CreatedDate'),
             'SystemModstamp':fields.datetime('SystemModstamp'),
             'price_entry_id':fields.char('Price Entry Id',size=64),
             'IsDeleted': fields.boolean('IsDeleted'),
             'salesforce_exportable': fields.boolean('SalesForce Exportable'),
             }
    _defaults = {
        'salesforce_exportable':False,
    }
    
#    delete corresponding product from salesforce

    def delete_product_from_salesforce(self,cr,uid,ids,context=None):
        
        """
        Delete the corresponding product from SalesForce
        @param cr: database cusrsor
        @param uid: id of the executing user
        @param ids: ids of the records       
        @return: response of salesforce
        """
                
        data=self.pool.get('salesforce.connection').get_active_saleforce_account_and_con(cr,uid) 
        account,con=data and data[0] # At present deleting the product only from one account.
        return self.delete_from_salesforce(cr, uid, con, account=account, ids=ids, sequence=0, context=context)


product_product()





