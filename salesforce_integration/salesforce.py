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

from openerp.osv import osv, fields
from openerp.tools.translate import _
# from osv import osv,fields
# from tools.translate import _
from api.salesforce import SalesforceAPI
from jinja2._stringdefs import No

from datetime import datetime

class salesforce_connection(osv.osv):
    _name="salesforce.connection"
    _description="""Stores the credentials of salesforce account """
    _columns={
        'name': fields.char('Account Name', size=64, required=True),
        'url': fields.char('URL', size=256),
        'username': fields.char('User Name', size=64,required=True),
        'password': fields.char('Password', size=64,required=True),
        'token':fields.char('Token',size=100,required=True ,help="Security token provided by SalesForce.com"),
        'confirmed' : fields.boolean('Confirmed',readonly=True),
        'timezone': fields.char('Time Zone', size=256),
        'currency_id' :  fields.many2one('res.currency',"Currency"),
        'lang_id' : fields.many2one('res.lang',"Language"),
        "company_name" : fields.char('Organization Name', size=128 ),
        "salesforce_data" :fields.text("SalesForce Information"),
        'version': fields.text("SalesForce Version")
    } 
    _defaults= {
                 "version" : "27.0",
               }  


#    Override the default write method -- user chnaged any credentials then set confirmed = false

    def write(self, cr, uid, ids, vals, context=None):
       if 'username' in vals or 'password' in vals or 'token' in vals:
           vals.update({'confirmed':False})
       return super(salesforce_connection, self).write(cr, uid, ids, vals, context=context)
       
    def login_salesforce(self, username, password,token,test_connection=False,context=None):
        
        """
        login to SalesForce account with given credentials
        @param username: SalesForce UserName
        @param password: SalesForce Password
        @param token: SalesForce Token
        @return: SalesForce  LoginResult object or raise an exception
        """
                
        print "login_salesforce context", context
        con = SalesforceAPI(username, password,token, context)
        success,response = con.login()
        if success :
            if test_connection:
                return response
            else:   
                return con
        raise osv.except_osv(_(response['errorCode']), _(response['message']))    
        return False
        
        
#         Method to check whether the request is for test.salesforce.com or login.salesforce.com   
    def check_sandbox(self, url = None, context={}) :
        try:
            if "test" in url:
                context.update({'sandbox':True})
        except: 
            pass
        return context      
       
        
    
    # validate the connection  
    def test_connection(self,cr,uid,ids,context={}):
        
        """
        Test SalesForce connection using given credentials
        @param cr: database cusrsor
        @param uid: id of the executing user
        @param ids: ids of the records       
        @return: boolean value or raise an exception
        """
       
        
        data = self.browse(cr,uid,ids,context)[0]
        
        context = self.check_sandbox(data.url, context)

        response = self.login_salesforce(data.username, data.password, data.token, test_connection=True, context=context)
        vals= {'confirmed':True,'timezone':response.get('userTimeZone',False),'company_name':response.get('organizationName',False)}
        currency_ids = self.pool.get('res.currency').search(cr, uid, [('name','=',response['orgDefaultCurrencyIsoCode'])], context=context)
        if currency_ids :
           vals.update({'currency_id':currency_ids[0]})
        lang_ids = self.pool.get('res.lang').search(cr, uid, [('code','=',response['userLanguage'])], context=context)
        if lang_ids :
           vals.update({'lang_id':lang_ids[0]})
        return self.write(cr, uid, ids, vals, context=context)
        
        
    # To get active account and con, if id is passed it can return its account and con.
    
    
    def get_active_saleforce_account_and_con(self,cr,uid,ids=[],context={}):
        
        """
        Get all active SalesForce Account and its connections
        @param cr: database cusrsor
        @param uid: id of the executing user
        @param ids: ids of the records       
        @return: a tuple of SalesForce accounts and connection object
        """
       
        vals=[('confirmed','=',True)]
        if ids:
            if not isinstance(ids, (list,tuple)):
                ids=[ids]
            vals.append(('id','in',ids))
        con_ids=self.search(cr,uid,vals)
        if not con_ids:
            raise osv.except_osv(_('ERROR'), _('No Active connectors to SalesForce'))
        data=[]
        for con_id in con_ids:
            account = self.browse(cr,uid,con_id,context)
            
            print "con_id, account, account.url", con_id, account, account.url
            
            context = self.check_sandbox(account.url, context)
            
            print "get_active_saleforce_account_and_con, context", context
            
            con = self.login_salesforce(account.username, account.password, account.token, context=context)
            data.append((account,con))
        return data


   
#    Import Partners   from SalesForce

    def import_partners(self, cr, uid, ids, context={}):
                        
        """
        Import Partners from SalesForce
        @param cr: database cusrsor
        @param uid: id of the executing user
        @param ids: ids of the records       
        @return: Return a wizard
        """
        print "Time At starting ", datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        data = self.browse(cr,uid,ids,context)[0]
        
        context = self.check_sandbox(data.url, context)
          
        con = self.login_salesforce(data.username, data.password, data.token, context=context)

        print "Time After Login ", datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        
        cr.execute("""SELECT MAX(updated_on) from salesforce_reference""")
        last_sync_date = cr.fetchone()
        

        if not last_sync_date:
            last_sync_date = ('2000-01-01 00:0:00',)
        
#         if last_sync_date
        result = self.pool.get('res.partner').import_all_from_salesforce(cr,uid,con,data) 

        print "Time After Account(Partner) import and creation in Openerp ", datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

        return result 
        
    #Export Partners to SalesForce        
    
    def export_partners(self, cr, uid, ids, context={}): 
    
                            
        """
        Export Partners to SalesForce
        @param cr: database cusrsor
        @param uid: id of the executing user
        @param ids: ids of the records       
        @return: Return a wizard or False
        """
       
       
        data = self.browse(cr,uid,ids,context)[0]
        
        print "export_partners"
        
        context = self.check_sandbox(data.url, context)
        
        print "context" , context
          
        obj_partner=self.pool.get('res.partner')
        
        print "EXPORT PARTNER - Time AT START OF SEARCHING OF PARTNER IDS", datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        partner_ids=obj_partner.search(cr,uid,[('customer','=',True),('id','in',obj_partner.salesforce_get_updated_ids(cr,uid,data)),('is_company','=',True)])
        print "EXPORT PARTNER - Time AFTER SEARCHING OF PARTNER IDS", datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        
        if partner_ids:
            con = self.login_salesforce(data.username, data.password, data.token, context=context)      
            return obj_partner.export_to_salesforce(cr, uid, con,data,partner_ids)
        return False
      
#    Import Contacts from SalesForce        

    def import_contacts(self, cr, uid, ids, context={}):
                        
        """
        Import Leads from SalesForce
        @param cr: database cusrsor
        @param uid: id of the executing user
        @param ids: ids of the records       
        @return: Return a wizard
        """
       
       
        print "Time At starting ", datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

        data = self.browse(cr,uid,ids,context)[0]
        
        print data
        
        context = self.check_sandbox(data.url, context)
          
        con = self.login_salesforce(data.username, data.password, data.token, context=context)
        print "Time After Login ", datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

        cr.execute("""SELECT MAX(updated_on) from salesforce_reference""")
        last_sync_date = cr.fetchone()

        if not last_sync_date:
            last_sync_date = ('2000-01-01 00:0:00',)
        
        result = self.pool.get('res.partner').import_all_from_salesforce(cr,uid,con,data,sequence=1, last_synced_on = last_sync_date)
        print "Time After Account(Partner) import and creation in Openerp ", datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

        return result

#    Export Contacts to SalesForce

    def export_contacts(self, cr, uid, ids, context={}):
                        
        """
        Export contacts SalesForce
        @param cr: database cusrsor
        @param uid: id of the executing user
        @param ids: ids of the records       
        @return: Return a wizard or False
        """
       
        data = self.browse(cr,uid,ids,context)[0]  
        
        print "export_contacts"
        
        context = self.check_sandbox(data.url, context)
        print "context" , context
        obj_partner=self.pool.get('res.partner')
        partner_ids=obj_partner.search(cr,uid,[('customer','=',True),('id','in',obj_partner.salesforce_get_updated_ids(cr,uid,data)),('is_company','=',False)])

#         print "partner_ids, salesforce_get_updated_ids", partner_ids[0]
        
        if partner_ids:
            con = self.login_salesforce(data.username, data.password, data.token, context=context)  
            return obj_partner.export_to_salesforce(cr,uid,con,data,partner_ids,1)
        return False
    
#    Import oppertunities from SalesForce

    def import_opportunities(self, cr, uid, ids, context={}):    
                        
        """
        Import Leads from SalesForce        
        @param cr: database cusrsor
        @param uid: id of the executing user
        @param ids: ids of the records       
        @return: Return a wizard
        """
              
        data = self.browse(cr,uid,ids,context)[0]
        
        context = self.check_sandbox(data.url, context)
          
        con = self.login_salesforce(data.username, data.password, data.token, context=context)
        return self.pool.get('crm.lead').import_all_from_salesforce(cr,uid,con,data,sequence=1)
        
#    Export oppertunites to SalesForce        

    def export_opportunities(self,cr,uid,ids,context={}):
                        
        """
        Export Opportunities to SalesForce
        @param cr: database cusrsor
        @param uid: id of the executing user
        @param ids: ids of the records       
        @return: Return a wizard
        """
       
       
        data = self.browse(cr,uid,ids,context)[0]
        
        context = self.check_sandbox(data.url, context)
                  
        obj_opportunity=self.pool.get('crm.lead')
        opportunity_ids=obj_opportunity.search(cr,uid,[('type','=','opportunity'),('id','in',obj_opportunity.salesforce_get_updated_ids(cr,uid,data))])
        #keep associated customer is not a child account otherwise sf integrity error
        if opportunity_ids:
            con = self.login_salesforce(data.username, data.password, data.token, context=context)
            return obj_opportunity.export_to_salesforce(cr, uid, con,data,opportunity_ids,1)
        return False
        
#    import Contracts from SalesForce        

    def import_contracts(self, cr, uid, ids, context={}):
                        
        """
        Import Contracts from SalesForce
        @param cr: database cusrsor
        @param uid: id of the executing user
        @param ids: ids of the records       
        @return: Return a wizard
        """
       
       
        data = self.browse(cr,uid,ids,context)[0]
        
        context = self.check_sandbox(data.url, context)
          
        con = self.login_salesforce(data.username, data.password, data.token, context=context)
        return self.pool.get('account.analytic.account').import_all_from_salesforce(cr,uid,con,data)
        
    #Export Contracts to SalesForce 
    def export_contracts(self,cr,uid,ids,context={}):
                        
        """
        Export Contracts to SalesForce
        @param cr: database cusrsor
        @param uid: id of the executing user
        @param ids: ids of the records       
        @return: Return a wizard
        """
              
        data = self.browse(cr,uid,ids,context)[0]
        
        context = self.check_sandbox(data.url, context)
                         
        con = self.login_salesforce(data.username, data.password, data.token, context=context)
        return self.pool.get('account.analytic.account').export_to_salesforce(cr, uid, con,data)
