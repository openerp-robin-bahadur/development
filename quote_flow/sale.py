from openerp.osv import fields, osv
from openerp.tools.translate import _

class sale_order(osv.osv):
    _inherit='sale.order'
    _description='Quotation Flow'


    STATE_SELECTION = [
        ('review', 'Review'),
        ('approved','Approved'),
        ('request_for_signature','Waiting for Signature'),
        ('draft', 'Draft Quotation'),
        ('sent', 'Quotation Sent'),
        ('cancel', 'Cancelled'),
        ('waiting_date', 'Waiting Schedule'),
        ('progress', 'Sales Order'),
        ('manual', 'Sale to Invoice'),
        ('invoice_except', 'Invoice Exception'),
        ('done', 'Done')]

    _columns={
#    'state_new':fields.selection([('review','Review'),
#                                ('approved','Approved'),
#                                ('request_for_signature','Waiting for Signature'),
##                                ('waiting_approved_signature','Waiting for Signature')
#                                ])
     'state': fields.selection([
        ('review', 'Review'),
        ('approved','Approved'),
        ('request_for_signature','Waiting for Signature'),
        ('draft', 'Draft Quotation'),
        ('sent', 'Quotation Sent'),
        ('cancel', 'Cancelled'),
        ('waiting_date', 'Waiting Schedule'),
        ('progress', 'Sales Order'),
        ('manual', 'Sale to Invoice'),
        ('invoice_except', 'Invoice Exception'),
        ('done', 'Done')], 'Status', readonly=True, track_visibility='onchange',
            help="Gives the status of the quotation or sales order. \nThe exception status is automatically set when a cancel operation occurs in the processing of a document linked to the sales order. \nThe 'Waiting Schedule' status is set when the invoice is confirmed but waiting for the scheduler to run on the order date.", select=True),


    }


    def action_review(self, cr, uid, ids, context=None):
        print "action_review======="
        self.write(cr, uid, ids, {'state': 'review'}, context=context)
        return True

sale_order()

