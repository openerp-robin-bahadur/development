from openerp.osv import fields,osv, expression
import time


class groups(osv.osv):
    _inherit = "res.groups"
    
    _columns = {
                'notify_email':fields.selection([('notify_account','Notify to Accountant'),('notify_manager','Notify to Manager'),('notify_both','Notify to Accountant & Manager')],'Quote Notification'),
                }