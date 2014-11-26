from openerp.osv import osv, fields
from openerp.tools.translate import _
import logging
import time

class salesforce_tables(osv.osv):
    _name="salesforce.tables"
    _description='SlaesForce Mapping Table Details'
    _rec_name='model'
    _columns={
        'model_id':fields.many2one('ir.model','Model',required='1'),
        'model':fields.char('Model Name',size=80 ),
        'salesforce_model':fields.char('SalesForce Record',size=80 ,required='1'), 
        'salesforce_field_ids':fields.one2many('salesforce.fields','table_id','Fields' ),
        'sequence' : fields.integer('Sequence'),      
    }
    
#    Override default create method -- add model name to filed model

    def create(self, cr, uid, vals, context=None):       
       model = self.pool.get('ir.model').browse(cr,uid,vals['model_id'])
       vals.update({'model':model.model})
       return super(salesforce_tables, self).create(cr, uid, vals, context=context)

#    Override default write method -- add model name to filed model
       
    def write(self, cr, uid, ids, vals, context=None):
       if 'model_id' in vals:
           model = self.pool.get('ir.model').browse(cr,uid,vals['model_id'])
           vals.update({'model':model.model})
       return super(salesforce_tables, self).write(cr, uid, ids, vals, context=context)   

#    Override default name_get method
       
    def name_get(self, cr, uid, ids, context=None):
        if isinstance(ids, (list, tuple)) and not len(ids):return []
        if isinstance(ids, (long, int)):ids = [ids]
        res = []
        for record in self.browse(cr, uid, ids,  context=context):
            res.append((record['id'], record.model_id.name or record.model_id.model))
        return res 
        
salesforce_tables()     

class salesforce_fields(osv.osv):
    _name="salesforce.fields"
    _description='SlaesForce Mapping Field Details'   
    _rec_name='field_id'
    _columns={
        'table_id':fields.many2one('salesforce.tables','Record' ,ondelete='cascade'),
        'field_id': fields.many2one('ir.model.fields', 'Field', ondelete='cascade' ,required='1'),
        'name':fields.related('field_id', 'name', type='char', string='Name'),
        'salesforce_name':fields.char('SalesForce Field',size=128 ,required='1'),
        'type': fields.selection([('in_out', 'Two way'), ('in', 'Import only'), ('out', 'Export only')], 'Type'),       
        'evaluation_type': fields.selection([('function', 'Function'), ('direct', 'Direct Mapping')], 'Evalution Type'), 
        'in_function': fields.text('Import Function'),
        'out_function': fields.text('Export Function'),      
    }
    _defaults = {
        'type': 'in_out',
        'evaluation_type':'direct'
    }
salesforce_fields()  


class salesforce_reference(osv.osv):
    _name="salesforce.reference"
    _description="SalesForce Syncing Reference"
    _columns={
        'model_id': fields.many2one('ir.model','Erp Model'),
        'model': fields.char( 'ERP Model', size=128,required=True ),
        'internal_id' :fields.integer('ERP Id',ondelete='cascade'),
        'salesforce_id':fields.char('SalesForce Id',size=80),
        'account_id':fields.many2one('salesforce.connection','SalesForce Account'),
        'updated_on':fields.datetime('Last Update On'),
        'sequence':fields.integer('Sequence'),
        'active':fields.boolean('Active')      
    }
    _defaults = {
        'updated_on': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'active' : True
    }
salesforce_reference()
