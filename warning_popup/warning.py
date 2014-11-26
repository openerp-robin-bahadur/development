

from openerp.osv import fields,osv
from openerp.tools.translate import _

class warning_message(osv.osv_memory):
    _name = "warning.message"
    _description = "show warning message"
    _columns = {
        'title': fields.char("Title",size=64,required=True),
        'message': fields.text("Message",required=True),
    }
    
    def show_message(self, cr, uid, title,message, context={}):
        """
            Show a warning msg to the user 
            @param cr : database cusrsor
            @param uid : user id 
            @param title : Pop up title
            @param mesage : popup message
            @return popup wizard
        """
        id = self.create(cr,uid, {'title': title, 'message': message},context=context)
        mod_obj = self.pool.get('ir.model.data')
        view = mod_obj.get_object_reference(cr, uid, 'warning_popup', 'view_warning_message')
        view_id = view and view[1] or False,
        res = {
            'name':  _(title),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'res_model': 'warning.message',
            'domain': [],
            'context': context,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': id
        }
        return res
        
warning_message()
