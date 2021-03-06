import requests
import xmltodict
import urlparse  
import json
import ast
from datetime import datetime


def getvalue_from_xml(dom, element):
   elementsByName = dom.getElementsByTagName(element)
   if len(elementsByName) > 0:
       elementValue = elementsByName[0].toxml().replace('<' + element + '>','').replace('</' + element + '>','')
   return  elementValue
   
# Base class which talks to SalesForce API 
class SalesforceAPI(object):

    def __init__(self, username, password, token, context = None, **kwargs):
        print "kwargs", kwargs
        self.username = username
        self.password = password
        self.token = token
        
        self._session = kwargs.get('session', False)
        self._instance = kwargs.get('instance', False)
        self._version = kwargs.get('version', '27.0')

        try:
            self._sandbox = context.get('sandbox', False)
        except:
            self._sandbox = kwargs.get('sandbox', False)
        
        self._headers = {
                       'Content-Type': 'application/json',
                       'Authorization': 'Bearer ' + str(self._session),
                       'X-PrettyPrint': '1'
                       }
        self._baseurl =  str(self._instance)+"/services/data/v"+str(self._version)+"/" 
        
    def get_session(self):
        return self._session    
        
    def set_session(self, session):
        self._session = session
        
    def get_instance(self):
        return self._instance
    
    def set_instance(self, instance):
        self._instance = instance
        
    def get_version(self):
        return self._version
    
    def set_version(self, version):
        self._version = version
    
    def get_headers(self):
        return self._headers
    
    def set_headers(self, headers):
        self._headers = headers
             
    def get_baseurl(self):
        return self._baseurl
    
    def set_baseurl(self, baseurl):
        self._baseurl = baseurl  
          
    def set_config(self, session, instance):
        """
            set the basic configuration parameters required for API calls
            @parms session : Saleforce API session, received while login
            @parms instance : Saleforce API instance ie , received while login , used to build API URL
            
        """
        self.set_session(session)
        self.set_instance(instance)
        self._headers = {
                       'Content-Type': 'application/json',
                       'Authorization': 'Bearer ' + str(self._session),
                       'X-PrettyPrint': '1'
                       }
        self._baseurl =  str(self._instance)+"/services/data/v"+str(self._version)+"/" 
        
              
    def login(self):   
        
        """
           Login to the Salesforce API
           this function use the configuration parameters and login to API 
           @return : loin status , response
        """
        
        # build the Login URL 
        url = 'https://login.salesforce.com/services/Soap/u/'+self.get_version()
        if self._sandbox :
           print "self._sandbox------",self._sandbox
           url =  'https://test.salesforce.com/services/Soap/u/'+self.get_version()
        
        # build the data to be passed to SalesforceAPI for login   
        body = """<?xml version="1.0" encoding="utf-8" ?>
                  <env:Envelope  xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:env="http://schemas.xmlsoap.org/soap/envelope/">
                      <env:Body>
                          <n1:login xmlns:n1="urn:partner.soap.sforce.com">
                              <n1:username>%s</n1:username>
                              <n1:password>%s%s</n1:password>
                          </n1:login>
                      </env:Body>
                 </env:Envelope>""" %(self.username, self.password, self.token)
                 
        status_code, response = self._request(url=url, body=body,method="POST",is_login=True)
        
        print response
        # convert the XMl to resposnse to Dict
        response = xmltodict.parse(response,dict_constructor=dict,xml_attribs=False)['soapenv:Envelope']['soapenv:Body']

        if status_code == 200 :  # if the login is success set the session and instance
            loginResponse= response['loginResponse']['result']
            session = loginResponse['sessionId']
            serverUrl = urlparse.urlparse(loginResponse['serverUrl'])
            instance = loginResponse['serverUrl'].replace('http://', '').replace('https://', '').split('/')[0].replace('-api', '')
            self.set_config(session, serverUrl[0]+"://"+serverUrl[1])
            return True,loginResponse['userInfo']
        else :
            error =response['soapenv:Fault']['detail'].get('LoginFault') and response['soapenv:Fault']['detail']['sf:LoginFault'] or response['soapenv:Fault']['detail']['sf:UnexpectedErrorFault']
            return False,{'errorCode':error['sf:exceptionCode'],'message':error['sf:exceptionMessage']} 
     
            
    def get_objectURL(self,object_name):  
        """
            Build the URl for given object
            @params object_name  : Name of th object eg : lead, account etc 
            @return : Final url for API call
        """
        return self.get_baseurl() + 'sobjects/'+object_name+'/' 
         
         
    def describe(self,object_name):
        ''' 
           Calls the describe SalesforceAPI to get the name of all fileds
           @params object_name  : Name of th object eg : lead, account etc 
           @return : response Status,response content
        '''
        url = self.get_objectURL(object_name) + 'describe'
        status_code, response = self._request(url=url,method="GET")  
        if status_code == 200 :
            
            return True,response
        else :  
            return False,response 
            
    def allfields_query(self,object_name, last_synced_on = False) :
        """ 
           Buld a query to SalesforceAPI which can retrieve all the fileds in a given object
           @params object_name  : Name of th object eg : lead, account etc 
           @return : response  query or False
        """
        success, fields = self.describe(object_name)
#         fo = open("/home/openerp/PArtner-logfrom_salesforce-3.txt", "rw+")
#         print success
#         print type(fields)
#         print ast.literal_eval(u"{'code1':1,'code2':1}")
        field_string=''
     
#         fo.write(rfields)
        if success:
            print type(fields) 
            for field in fields['fields'] :
#                 print field
#                 fo1 = open("/home/openerp/PArtner-logfrom_salesforce-2.txt", "rw+")
#                 fo1.write(field)
                field_string += field['name']+','
            field_string  = field_string[:-1]
#             print "field_string------",field_string
            if last_synced_on:
                last_synced_on = datetime.strptime(last_synced_on[0],'%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%dT%H:%M:%S') + '.000+0000'
            print "last_synced_on", last_synced_on
            
#             last_synced_on = ("2013-10-25T19:09:46.000+0000", )
#             where_clause = last_synced_on != False and "WHERE LastModifiedDate >= "+ last_synced_on[0] +" or CreatedDate >= '"+last_synced_on[0]  or ""
            where_clause = last_synced_on != False and "WHERE LastModifiedDate >= "+ last_synced_on +" or CreatedDate >= " + last_synced_on   or ""
            query= "SELECT "+field_string+ " FROM "+object_name  + " " + where_clause
            
            print "Final request query", query
 
            return query
        return False    
                   
    def read_allfields(self,object_name, single_page=False, last_synced_on = False):
        """ 
           Retrive the all the fields value from SalesforceAPI
           @params object_name  : Name of th object eg : lead, account etc 
           @params single page  : True or False, used to identofy if ther is pagination required 
           @return : response  or error msg
        """ 
        query = self.allfields_query(object_name, last_synced_on = last_synced_on)
        
#         print "Query to Salesforce", query
        
        
        if query :
            if single_page:   # if single page return the response
                return   self.read_records(query) 
                
            return   self.read_all_records(query)    # call the API recusrsively and read the data 
        return False,{'errorCode':"ERROR IN FIELDS",'message':"There was some error in mapping the fields"} 
            
    def read_record(self,object_name,record_id):  
        """ 
           Retrive a record for a given id in an object
           @params object_name  : Name of th object eg : lead, account etc 
           @params record_id  : ID of the record
           @return : status, response  
        """  
        url = self.get_objectURL(object_name) + record_id
        status_code, response = self._request(url=url,method="GET") 
        if status_code == 200 :
            return True,response
        else :  
            return False,response 
             
    def read_records_with_url(self,query_url):
        """ 
           Retrive data from salesforce for the given query
           @params query_url  : query used to appened with URL
           @return : status, response  
        """  
        url = self.get_instance() + query_url 
        status_code, response = self._request(url=url,method="GET") 
        if status_code == 200 :
            return True,response
        else :  
            return False,response     
            
    def read_records(self,query):
        """ 
           Retrive a single page result from salesforce for the given query
           @params query  : query used retrieve data, passed a param to SalesforceAPI
           @return : status, response  
        """ 
        url = self.get_baseurl() + 'query/'
        params = {'q': query}
        print "params", params, url
        status_code, response = self._request(url=url,method="GET",params=params)  
        print "SAlesforce Record ", response
        if status_code == 200 :
            return True,response
        else :  
            return False,response  
            
    def read_all_records(self,query):  
        """
            Get the complete records from Salesforce by calling the api recusrsively
            @params query  : query used retrieve data
            @return : status, response  
        """
        # recursive function which calls the next page
        def get_next_page_result(last_page):
        
            # if the last pages status is done then no more records are available, so return the last page
            if last_page['done']:
                return last_page
            #if more pags are available call the next page with nextRecordsUrl , available in last page response    
            else:
                #Call the next page with read_records_with_url function
                status,current_page = self.read_records_with_url(last_page['nextRecordsUrl'])
                
                if not status:   # if failed retrun the last page
                    return last_page
                    
                # merge the results    
                current_page['totalSize'] += last_page['totalSize']
                last_page['records'].extend(current_page['records'])
                current_page['records'] = last_page['records']
                
                # Continue the recursion
                return get_next_page_result(current_page)
        
        # get the first page by normal querying of API        
        success,result = self.read_records(query)
        
        if success :   # if response is sucess the call the next page
            return True,get_next_page_result(result)['records']
            
        return success,result  
    
    # 	Search function
    def search(self,search_query):
        """
            Search string that specifies the text expression to search for, the scope of fields to search, the list of objects and fields. 
            to retrieve, and the maximum number of records to return.
            
            Eg  " FIND {4159017000} IN Phone FIELDS RETURNING "
                + "Contact(Id, Phone, FirstName, LastName), "
                + "Lead(Id, Phone, FirstName, LastName), "
                + "Account(Id, Phone, Name)"
              will  returns contacts, leads, and accounts whose phone fields contain a specified value  
           @params query  : query used retrieve data
           @return : status, response     
        """
        url = self.get_baseurl() + 'search/'
        params = {'q': search_query}
        status_code, response = self._request(url=url,method="GET",params=params)   
        if status_code == 200 :
            return True,response
        else :  
            return False,response
            
    def create_record(self, object_name, record_data):
        """
            Create a records in  Salesforce for a given object
            @params object_name  : Name of th object eg : lead, account etc 
            @params record_data  :  Data to be created
            @return : status, created ID  or error msg
        """
        url = self.get_objectURL(object_name)
        status_code, response = self._request(url=url, method="POST", body=json.dumps(record_data))   # POST the json format data
        if status_code == 200 or status_code == 201  :
            if response['success']:
                return True,response['id']
            else:
                return False,{'errorCode':"ERROR IN CREATE",'message':response['errors']} 
        else :  
            return False,response     
             
    def update_record(self, object_name, record_id, record_data):
        """
            Update a records with given ID in  Salesforce for a given object
            @params object_name  : Name of th object eg : lead, account etc 
            @params record_id  :  SalesForce ID
            @params record_data  :  Data to be created
            @return : status, response  or error msg
        """
        url = self.get_objectURL(object_name) + record_id
        status_code, response = self._request(url=url, method="PATCH", body=json.dumps(record_data))   # PATCH the json format data
        if status_code == 200 or status_code == 201  or status_code == 204 :
            return True,response
        else :  
            return False,response  
            
    def delete_record(self, object_name, record_id):
        """
            Delete a records with given ID in  Salesforce for a given object
            @params object_name  : Name of th object eg : lead, account etc 
            @params record_id  :  SalesForce ID
            @return : status, response  or error msg
        """
        url = self.get_objectURL(object_name) + record_id
        status_code, response = self._request(url=url, method="DELETE")   
        if status_code == 200 or status_code == 204 :
            return True,response
        else :  
            return False,response    
                                         
    def _request(self, url='', body='', method="POST",params={},is_login=False):
        """
            This is the function whcih is responsible for sendnig requests to SalesforceAPI
            @params url  : SalesForce API URL 
            @params body  :  Request Body 
            @params method  :  Request method , POST for create , GET for read, PATCH for update DELETE for delete 
            @return : status code, response content
        """
        headers =  self.get_headers()    # get the defult header
        
        if is_login :  # if its logion request Use login header
            headers=  {
                      'content-type': 'text/xml',
                      'charset': 'UTF-8',
                      'SOAPAction': 'login'
                     }
 
        if not url: # if no URL is passed get the default  Base URl
            url =   self.get_baseurl()
            
        response = requests.request(method, url, data=body,params=params, headers=headers)
        content = response.content
        print "----------------------"
#         print response.content
        print "----------------------"
        if not is_login and content:
       
#            content = response.json()
           try:
              content = json.loads(response.content)
#               response.json()   # if login get the josn value of response
           except Exception:
                print str(Exception) 
#                 print content
                content=  eval(content)
#                   pass
           if  isinstance(content, (list,tuple)): # if response is arraay get the first element
                  content=content[0]
        return  response.status_code, content
        
        


