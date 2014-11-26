from openerp.osv import osv, fields
from openerp.tools.translate import _
import logging
import time
import pooler
from datetime import datetime

class log_details(osv.osv):
    _name = 'log.details'
    _description = 'Logs details'
    _order = 'log_date desc'

    _columns = {
        'log_date': fields.datetime('Time', readonly=True),
        'log_uid': fields.many2one('res.users', "User"),
        'res_id': fields.integer('Ressource id', readonly=True),
        'log_res_name': fields.char('Resource name', size=156, readonly=True),
        'connector':fields.char('Connector', size=156, readonly=True),
        'model_name': fields.char('Model name', size=64, readonly=True),
        'message': fields.text('Message', readonly=True),
        'type':fields.selection([('import','Import'),('export','Export'),('delete','Delete'),],'Action', readonly=True),
        'state':fields.selection([('info','Info'),('error','Error')],'State', readonly=True),
        'module':fields.char('Module', size=64, readonly=True),
    }
    _defaults = {
        'log_date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S')
    }
    
#    save error log 


    def register_log(self, cr, uid, module='', connector_name='', model='', res_id=0, sync_type='import', message='', state='info',context={}):
        """
           register a log in openerp server
           
        """ 
        db =cr.dbname
        cursor = pooler.get_db(db).cursor()
        logger = logging.getLogger(model)
        if state == 'error':
            logger.error('%s for %s >> %s'%(sync_type, connector_name, message))
        else:
            logger.info('%s for %s >> %s'%(sync_type, connector_name, message))
        if not model:return True
        self.create(cursor, uid, {
                              'log_uid':uid,
                              'res_id':res_id,
#                              'log_res_name':self.pool.get(model).browse(cr,uid,res_id).name,
                              'model_name':model,
                              'connector':connector_name,
                              'message':message,
                              'state':state,
                              'type':sync_type,
                              'module':module
                             })
        cursor.commit()
        cursor.close()                     
                             
log_details()
