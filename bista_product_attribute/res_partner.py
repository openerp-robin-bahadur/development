from openerp.osv import osv, fields
import time
from datetime import datetime, timedelta
from openerp.tools.float_utils import float_round as round
import openerp.addons.decimal_precision as dp



class res_partner(osv.osv):
    _inherit= "res.partner"

#    def _get_report_code(self, cr, uid, context=None):
#       reprt_obj = self.pool.get('ir.actions.report.xml')
#       ids = reprt_obj.search(cr, uid, [('model','=','sale.order')])
#       res = reprt_obj.read(cr, uid, ids, ['report_name', 'name'], context=context)
#       return [(r['report_name'], r['name']) for r in res]

    _columns={
        'x_vendor_id':fields.char('Vendor Id', size=128),
        'x_ein': fields.char('Employer Identification No',size=128),
        'x_street_3': fields.char('Street 3', size=128),



#        custo field according to send file 29-8-2014



        'x_is_billing_vendor':fields.boolean('Is Billing Vendor'),
        'x_quote_terms':fields.text('Quote Terms'),
#        'x_report_type':fields.selection(_get_report_code,string='Report Type'),
        



    }

#    _sql_constraints = [
#        ('vendor_uniq', 'unique(x_vendor_id)', 'Vendor ID should be unique!'),
#    ]


res_partner()