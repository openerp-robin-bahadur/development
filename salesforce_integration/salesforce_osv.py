from openerp.osv import osv
from openerp.osv import fields
from openerp.tools.translate import _
import time 
from openerp import pooler

from datetime import datetime

def get_salesforce_account(self, cr, uid, context=None):
        
    """
    Get SalesForce account details
    @param cr: database cusrsor
    @param uid: id of the executing user     
    @return: browse record object
    """
        
    acc_obj = self.pool.get("salesforce.connection")
    acc_ids = acc_obj.search(cr, uid, [('confirmed','=',True)],context=context)# get confirmed SalesForce connection 
    if not acc_ids :
       raise osv.except_osv(_("Error "),_("There is no active salesforce connection defined.\n Please add a salesforce connection and try again"))
    return  acc_obj.browse(cr,uid,acc_ids,context=context)[0]#browse 
 
#Get SalesForce resource (Table) 
      
def get_salesforce_resource(self, cr, uid, sequence=0, context=None):
    """
    Search if a coneection to a given module is available
    if yes return that resouce from salesforce.table
    if not raise exception
    @param cr: database cusrsor
    @param uid: id of the executing user   
    @param sequence: sequence of the data, default is 0  
    @return: dictionary
    
    """
    if not context:
        context={}
    resource_obj = self.pool.get('salesforce.tables')
    # search for  the given model and sequence in salesforce.table
    resource_ids= resource_obj.search(cr, uid, [('model','=',self._name),('sequence','=',sequence)],context=context)
    
    if not resource_ids :   # if no refernce found raise the error
        raise osv.except_osv(_("Error "),_("Saleforce connector is not available for this resource %s " %self._name))  
    
    # read that record and return    
    resource= resource_obj.read(cr, uid, resource_ids,[],context=context)[0]
    return resource
    

def get_salesforce_field_mapping(self, cr, uid, table_id, move="in", context=None):

    """
    Get all the fields from salesforce.fields in a given model and return back
    depending up on move "in" or "out this method will return the corresponding fields"
    @param cr: database cusrsor
    @param uid: id of the executing user  
    @param table_id: SalesForce table id --'salesforce.tables'
    @param move:    type of the method -- values 'in','out'
    @return: dictionary
    """
    
    if not context:
        context={}
    
    filter_string = [('table_id','=',table_id),('type','in',['in_out',move])]
    sf_field_pool = self.pool.get('salesforce.fields')
    field_ids = sf_field_pool.search(cr, uid, filter_string,context=context)
    
    if field_ids :  # if field is found read the values
        fields = sf_field_pool.read(cr, uid, field_ids, context=context)
    else:    # in no field found set the fileds as empty list
       fields = []
       
    result={}   
    # depending on move type prepare the dict key 
    key = move == 'in' and 'salesforce_name' or 'name'
    for field in fields :
        result[field[key]]= field     # for import dict key will be salesforce filed name and Internal filed name for export
    return result
    
# method to prapare a salesforce API (THis is not used )    
def prepare_salesforce_query(resource, fields, context=None):
    """
    Generat Query for SalesForce
    @param resource: SalesForce Table name
    @param fields: fields list
    @return: string
    """
        
    field_string ="" 
    for field in fields.keys():
       field_string += field+','
    field_string  += "Id"  
    query= "SELECT "+field_string+ " FROM "+resource
    return query 
       
def salesforce_import_mapping(self, cr, uid, response, fields, con, account=False, context=None): 
    """
        Map the fields to import ,
        ARGS : cr : database cursor
               uid : ID the user 
               response : API response dict from Salesforce
               fields : fields dict prepared by get_salesforce_field_mapping()
:              con : connection object to salesforce api 
        Return  : dict which is ready to be wriiten or created a record            
    """ 
    res = {}
    # iterate through the fileds 
    for key,value in fields.items():
    
        if  value['evaluation_type'] == 'direct' : #if the field is directy mapping type the assing the value from response
            res[value['name']]= response.get(key,False)
         
        elif  value['evaluation_type'] == 'function' :  # if its functional filed execute the function
            space = { 'self': self,
                      'cr': cr,
                      'uid': uid,
                      'key': key,
                      'response': response,
                      'con' : con,
                      'account' : account,
                      'context':context,         
                        }        # these are the variables which will be availble in functions
            try: 
                exec value['in_function'] in space   # execute the functions
            except Exception, e:   # If there is any execpion catch that 
                raise osv.except_osv(_("Error "),_(e))  
                
            result = space.get('result', False)   # the ooutput of the function should be in variable result
            
            if result: # If there is any result add that to res dict
                if isinstance(result, list): 
                    for each_tuple in result:
                        if isinstance(each_tuple, tuple) and len(each_tuple) == 2:
                            res[each_tuple[0]] = each_tuple[1]
        else :  # if the field is ot found assign it as false
            res[value['name']]= False
            
    return res  # return the dict 
    
def import_from_salesforce(self, cr, uid, internal_id, con, account=False, sequence=0, context=None):  

    if not context:
        context = {}
    salesforce_id =self.get_internal_reference(cr, uid, account.id, internal_id, sequence=sequence, context=context)
    
def import_from_salesforce(self, cr, uid,  con, ids, account=False, sequence=0, context=None): 
    if not isinstance(ids, (list,tuple)):
         ids = [ids]    
    for id in ids :
         self.import_all_from_salesforce(cr, uid,  con, account=account, ids=ids, sequence=sequence, context=context) 
    return True   
      
def import_all_from_salesforce(self, cr, uid,  con, account=False, last_synced_on = False, ids=False, sequence=0, context=None):
    """
    Import all data from SalesForce
    @param cr: database cursor
    @param uid: id of the executing user  
    @param con: SalesForce  connection object
    @param account: SalesForce Account object
    @param ids: ids of the corresponding erp record
    @param sequence: SalesForce resouce sequence, default is 0
    @return: wizard
    """
    print "last_synced_on", last_synced_on
    if not context:
        context = {}
    if  isinstance(ids, (list,tuple)):
         ids = ids[0]   
    if not account:
       account = self.get_salesforce_account(cr,uid,context=context) 
    context.update({'tz':account.timezone})    
    resource = self.get_salesforce_resource(cr, uid, sequence=sequence, context=context)
    
      
    model=  resource['model']
    fields = self.get_salesforce_field_mapping(cr, uid, resource['id'], move="in", context=context)
    
    if not fields :
        raise osv.except_osv(_("Error "),_("No fileds mapped for the model %s " %self._name))  

    if ids :
        sf_id =self.get_selesforce_reference(cr, uid, account.id, ids, context=context)
        success,response = con.read_record(resource['salesforce_model'],str(sf_id))
        print type(response) 
        
    else :        
        success,response = con.read_allfields(resource['salesforce_model'] ,last_synced_on = last_synced_on)
        print type(response) 
    if not success :
        raise osv.except_osv(_(response['errorCode']),_(response['message']))
          
    if not isinstance(response, (list,tuple)):
         response = [response] 
         
    total_count =0
    create_count= 0
    update_count = 0            
    for result in response :
        total_count += 1
        salesforce_id = result['Id']
        vals =  self.salesforce_import_mapping(cr,uid,result,fields,con,account,context=context)
        print "salesforce_import_mapping vals", vals

        internal_id =self.get_internal_reference(cr, uid, account.id, salesforce_id, sequence=sequence, context=context)
        if internal_id :
            try:
                self.write(cr,uid,[internal_id],vals,context=context)
                self.set_salesforce_ref(cr, uid, account.id, internal_id, salesforce_id,sequence=sequence,context=context) 
                update_count += 1   
            except Exception as e:
                print e 
                self.pool.get('log.details').register_log(cr, uid, module='Saleforce', connector_name=account.name, model=resource['model_id'][1], res_id=internal_id, sync_type='import', message=_("Writing of import data Failed - %s"%e), state='error', context=context)
                cr.commit()     
        else : 
            try :
                internal_id = self.create(cr,uid,vals,context=context)
                self.set_salesforce_ref(cr, uid, account.id, internal_id, salesforce_id, sequence=sequence, context=context) 
                create_count += 1 
            except Exception as e:
                self.pool.get('log.details').register_log(cr, uid, module='Saleforce', connector_name=account.name, model=resource['model_id'][1], res_id=internal_id, sync_type='import', message=_("Creation of import data Failed - %s"%e), state='error', context=context)
                cr.commit()  
                     
    msg = 'Number of Records From SalesForce : '+ str(total_count) +'\nNumber of Records Created  : '+ str(create_count)+'\nNumber of Records Updated  : '+ str(update_count)+'\nNumber of Failed Imports  : '+ str(total_count-(update_count+create_count))+"\n\n Please find the log to see the error report of failed operations"
    title =  'Import ->'+ resource['model_id'][1]
    
    return self.pool.get('warning.message').show_message(cr,uid,_(title),_(msg))
    
    
def salesforce_get_updated_ids(self, cr, uid, account, ids=[], context={}):
    """
    Get Updated ids
    @param cr: database cursor
    @param uid: id of the executing user  
    @param account: SalesForce Account object
    @param ids: ids of the corresponding erp record   
    @return: list of ids
    """
    up_ids = []
    if ids:
        res_ids = ids
    else:   
        res_ids = self.search(cr, uid, [], context=context)
        
#     print "salesforce_get_updated_ids - res_ids()", len(res_ids)
#     print "@param account: SalesForce Account object", account
#     print "model ",self._name

    ref_pool = self.pool.get('salesforce.reference')
    
    cr.execute("""
                select internal_id 
                FROM 
                salesforce_reference 
                WHERE
                 model = '%s'and account_id = %d
    """ % (self._name, account.id))
   
    sf_ref_internal_id_dict = cr.dictfetchall()
    
    sf_ref_internal_id = []
    
    for each in sf_ref_internal_id_dict:
        sf_ref_internal_id.append(each['internal_id'])
    
    up_ids += list(set(res_ids) - set(sf_ref_internal_id))
    print "New IDS need to be updated", len(up_ids)  
    sf_ref_internal_id = list(set(sf_ref_internal_id) & set(res_ids))
        
    print "Salesforcec internal ids", len(sf_ref_internal_id)
    
    cr.execute("""
    SELECT internal_id, updated_on 
    FROM salesforce_reference
    WHERE active = True AND internal_id in """ + str(tuple(sf_ref_internal_id))
     )
    
    sf_ids_last_updated = cr.fetchall()
    
    print "sf_ids_last_updated", len(sf_ids_last_updated)
    print datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    for each in sf_ids_last_updated:
        cur_id = self.search(cr, uid, [
               '|',
               ('write_date','>', each[1]),
               ('create_date','>',each[1]),
               ('id','=', each[0])
               ])
        if cur_id:
            up_ids.append(cur_id[0])
    print "Final IDS need to be updated", len(up_ids)  
    print datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    
        
#     sf_ref_internal_id = ref_pool.read(cr, uid, sf_ref_id ,['internal_id'])
    
    
#     for res_id in res_ids :
#         print "salesforce_get_updated_ids - res_ids()", res_id

#         ref_id = ref_pool.search(cr, uid, [
#                        ('model','=', self._name),
#                        ('internal_id', '=', res_id),
#                        ('account_id', '=', account.id),
#             ])
#         if not ref_id:
#             up_ids.append(res_id)
#             continue
         
#         reference = ref_pool.read(cr, uid,ref_id,['updated_on'], context=context)[0]
#         cur_id = self.search(cr, uid, [
#                 '|',
#                 ('write_date','>',reference['updated_on']),
#                 ('create_date','>',reference['updated_on']),
#                 ('id','=',res_id)
#         ])
# 
#         if cur_id:
# 
#             up_ids.append(cur_id[0])

    return up_ids
    

def salesforce_export_mapping(self, cr, uid, record, fields, con,account=False, context=None): 
    """
    SalesForce Export Mapping 
    @param cr: database cursor
    @param uid: id of the executing user 
    @param record: Data Object
    @param con: SalesForce Connection Object
    @param account: SalesForce Account object  
    @return: dictionary
    """    
    res= {} 
    for key,value in fields.items():
   
        if  value['evaluation_type'] == 'direct' and hasattr(record,key):
            res[value['salesforce_name']]= getattr(record,key) or None
               
        elif  value['evaluation_type'] == 'function' :  
            space = { 'self': self,
                      'cr': cr,
                      'uid': uid,
                      'key': key,
                      'record': record,
                      'con' : con,
                      'account':account,
                      'context':context,         
                        }   
            try:
                exec value['out_function'] in space
            except Exception, e:
                raise osv.except_osv(_("Error "),_(e))  
            result = space.get('result', False)  
            if result:
                if isinstance(result, list):
                    for each_tuple in result:
                        if isinstance(each_tuple, tuple) and len(each_tuple) == 2:
                            res[each_tuple[0]] = each_tuple[1]   
        else:
             res[value['salesforce_name']]= None
    return res
             
def export_to_salesforce(self, cr, uid,  con, account=False, ids=[], sequence=0, context=None):
    """
    Export to  SalesForce
    @param cr: database cursor
    @param uid: id of the executing user  
    @param con: SalesForce  connection object
    @param account: SalesForce Account object
    @param ids: ids of the corresponding erp record
    @param sequence: SalesForce resouce sequence, default is 0
    @return: wizard
    """
    if not context:
        context = {}
    if not account:
       account = self.get_salesforce_account(cr,uid,context=context)
    context.update({'tz':account.timezone})      
    resource = self.get_salesforce_resource(cr, uid, sequence=sequence, context=context)  
    model=  resource['model']
    fields = self.get_salesforce_field_mapping(cr, uid, resource['id'], move="out", context=context)
    if not fields :
        raise osv.except_osv(_("Error "),_("No fields mapped for the model %s " %self._name))    
    if not ids:    
        ids = self.salesforce_get_updated_ids(cr, uid, account, ids=ids, context = context )   
    if not ids:
        return False     
    total_count =0
    success_count= 0    
    for record in self.browse(cr, uid, ids, context = context) :
        total_count +=1
        vals =  self.salesforce_export_mapping(cr,uid,record,fields,con,account,context=context)
        salesforce_id = self.get_salesforce_reference(cr,uid, account.id, record.id, sequence=sequence, context=None) 
        print vals
        print salesforce_id
        if salesforce_id:
           print "START TIME AT EXPORT ONE ACCOUNT (UPDATE)", datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
           success,response = con.update_record(resource['salesforce_model'], salesforce_id, vals)
           print "END TIME AFTER EXPORT OF ONE ACCOUNT (UPDATE)", datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        else:
           print "START TIME AT EXPORT ONE ACCOUNT (CREATE)", datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
           success,response= con.create_record(resource['salesforce_model'], vals)    
           print "END TIME AFTER EXPORT OF ONE ACCOUNT (CREATE)", datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
           salesforce_id =response
        if success :
            self.set_salesforce_ref(cr, uid, account.id, record.id, salesforce_id , sequence=sequence, context=context)
            success_count += 1
        else :
            self.pool.get('log.details').register_log(cr, uid, module='Saleforce', connector_name=account.name, model=resource['model_id'][1], res_id=record.id, sync_type='export', message=_("Export failed - %s-%s"%(response['errorCode'],response['message'])), state='error', context=context)
            pass  
            
    msg = 'Number of Records Tried to Export : '+ str(total_count) +'\nNumber of Successed  Export : '+ str(success_count)+"\n\n Please find the log to see the error report of failed operations"
    title =  'Export ->'+ resource['model_id'][1]
    return self.pool.get('warning.message').show_message(cr,uid,_(title),_(msg))
      
        
def delete_from_salesforce(self, cr, uid, con, account=False, ids=[], sequence=0, context=None) :  
    """
    Delete from SalesForce
    @param cr: database cursor
    @param uid: id of the executing user  
    @param con: SalesForce  connection object
    @param account: SalesForce Account object
    @param ids: ids of the corresponding erp record
    @param sequence: SalesForce resouce sequence, default is 0
    @return: wizard
    """
    if not context:
        context = {}
    if not account:   
       account = self.get_salesforce_account(cr,uid,context=context)
    
    print "account ", account
    
    resource = self.get_salesforce_resource(cr, uid, sequence=sequence, context=context) 
    if ids :
        ref_obj=self.pool.get('salesforce.reference')
        total_count =0
        success_count= 0
        if not isinstance(ids, (list,tuple)):
            ids = [ids] 
        for res_id in ids:
            total_count += 1
            salesforce_id = self.get_salesforce_reference(cr,uid, account.id, res_id,  sequence=sequence, context=None)   
            if salesforce_id:
                success,response = con.delete_record(resource['salesforce_model'], salesforce_id)
                print success,response
                if success:
                    success_count += 1
                    ref_id=ref_obj.search(cr,uid,[('model','=',self._name),('internal_id','=',res_id),('account_id', '=', account.id),('sequence','=',sequence)])    
#                     ref_obj.unlink(cr, uid, ref_id, context=context)
                    ref_obj.write(cr, uid, ref_id, {'active':False}, context=context )
                    
                else:
                    self.pool.get('log.details').register_log(cr, uid, module='Saleforce', connector_name=account.name, model=resource['model_id'][1], res_id=res_id, sync_type='delete', message=_("Delete failed - %s-%s"%(response['errorCode'],response['message'])), state='error', context=context)
                    pass
            else:
                raise osv.except_osv(_("Error "),_("This record has already been deleted from SalesForce"))

        msg = 'Number of Records Tried to Delete : '+ str(total_count) +'\n Number of Successed  delete : '+ str(success_count)+"\n\n Please find the log to see the error report of failed deletion"
        title =  'Delete ->'+ resource['model_id'][1]
        return self.pool.get('warning.message').show_message(cr,uid,_(title),_(msg))     
    return True
                   
def set_salesforce_ref(self, cr, uid, account_id, internal_id, salesforce_id,sequence=0,context={}):
    """
    Set SalesForce reference
    @param cr: database cursor
    @param uid: id of the executing user      
    @param account_id: SalesForce Account object
    @param internal_id: erp id
    @param salesforce_id: salesforce id
    @param sequence: SalesForce resouce sequence, default is 0
    @return: True
    """
    #remove this comment
    """
        Set  the Salesforce ID for a resouce 
        ARGS:   account : salesforce aconnection account obj
                salesforce_id (int)  : salesforce id from API response
        result : res_id(int) or False        
     """
    ref_pool = self.pool.get('salesforce.reference')
    
    #search if its alreadt set
    ref_ids = ref_pool.search(cr, uid, [
                ('model','=', self._name),
                ('internal_id', '=', internal_id),
                ('account_id', '=', account_id),
                ('sequence', '=', sequence),
            ])
    updated_on = time.strftime('%Y-%m-%d %H:%M:%S')
    if ref_ids: # if alreadt set update the time
        
        ref_pool.write(cr, uid, ref_ids, {'salesforce_id':salesforce_id,'updated_on':updated_on,'sequence':sequence})

    else: # if new item create a reference
        
        ref_pool.create(cr, uid, {
                                  'model':self._name,
                                  'internal_id':internal_id,
                                  'account_id':account_id,
                                  'salesforce_id':salesforce_id,
                                  'updated_on':updated_on,
                                  'sequence':sequence,
                                  })

    return True

def get_internal_reference(self, cr, uid, account_id, salesforce_id, sequence=0, context=None):

    """
        Find the Internal ID of a given record from a salesforce ID
        ARGS:   account : salesforce aconnection account obj
                salesforce_id (int)  : salesforce id from API response
        result : res_id(int) or False        
     """

    ref_pool = self.pool.get('salesforce.reference')
    
    # search for a reference id for given condition
    ref_ids = ref_pool.search(cr, uid, [
                 ('model','=', self._name),
                ('salesforce_id', '=', salesforce_id),
                ('account_id', '=', account_id),
                ('sequence', '=', sequence), 
            ])
   
    if ref_ids: # if reference is available return the internal id
        ref_data = ref_pool.read(cr, uid, ref_ids, ['internal_id'],context=context)[0]
        return  ref_data['internal_id']    
        
    return False # Return False if no reference is available       
    

def get_salesforce_reference(self, cr, uid, account_id, internal_id, sequence=0, context=None):
    """
        Find the salesforce ID of a given internalID
        ARGS:   account : salesforce aconnection account obj
                internal_id (int)  : internal id  for record
        result : res_id(int) or False        
     """
    
    ref_pool = self.pool.get('salesforce.reference')
    
    # search for a reference id for given condition
    ref_ids = ref_pool.search(cr, uid, [
                 ('model','=', self._name),
                ('internal_id', '=', internal_id),
                ('account_id', '=', account_id),
                ('sequence', '=', sequence),
            ])
            
    if ref_ids: # if reference is available return the salesforce id
        ref_data = ref_pool.read(cr, uid, ref_ids, ['salesforce_id'],context=context)[0]
        return  ref_data['salesforce_id']    
        
    return False # Return False if no reference is available           

def unlinkasd(self, cr, uid, ids, context={}):
    """
        Delete from ERP and SalesForce
        @param cr: database cusrsor
        @param uid: id of the executing user
        @param ids: erp ids of the records to be deleted
        @return: True or Flase
    """ 
    deleted_ref_ids = []                                                               
    deleted = super(osv.osv, self).unlink(cr, uid, ids, context=context)
    resource_obj = self.pool.get('salesforce.tables')
    if resource_obj and resource_obj._columns.get('model'):
       resource_ids= resource_obj.search(cr, uid, [('model','=',self._name)],context=context) 
       sf_objs = self.pool.get('salesforce.connection').search(cr, uid, [('confirmed','=',True)], context=context)    
       if deleted and resource_ids  :                                                            
            for sf_obj in sf_objs :
                #delete from salesforce
                for id in ids:
                    sf_id = self.get_prestashop_ref(cr, uid, shop,id, context)
                    if sf_id : 
                       deleted_ref_ids.append(sf_id)
#                self.delete_from_salesforce(cr, uid, sf_objs, deleted_ref_ids,convert_to_presta_id=False,context=context)                                                                   
    return deleted  
osv.osv.get_salesforce_resource = get_salesforce_resource
osv.osv.get_salesforce_field_mapping = get_salesforce_field_mapping
osv.osv.salesforce_import_mapping = salesforce_import_mapping
osv.osv.import_all_from_salesforce = import_all_from_salesforce
osv.osv.import_from_salesforce = import_from_salesforce

osv.osv.export_to_salesforce = export_to_salesforce
osv.osv.salesforce_export_mapping = salesforce_export_mapping
osv.osv.salesforce_get_updated_ids = salesforce_get_updated_ids

osv.osv.set_salesforce_ref = set_salesforce_ref
osv.osv.get_internal_reference = get_internal_reference
osv.osv.get_salesforce_reference = get_salesforce_reference
osv.osv.get_salesforce_account= get_salesforce_account
osv.osv.delete_from_salesforce = delete_from_salesforce
