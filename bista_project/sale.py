from datetime import datetime, date
from openerp.osv import fields, osv
from openerp.tools.translate import _
from lxml import etree
from openerp.addons.base_status.base_stage import base_stage
from openerp.addons.resource.faces import task as Task

class sale(osv.osv_memory):
    _inherit = 'sale.order'

    def button_create_project(self, cr, uid, ids, context=None):
        so_obj=self.browse(cr, uid, ids, context)
        for each in so_obj:
            if each.x_signed_flag:
                self.pool.get('project.project').create_project(cr,uid,ids,context)


sale()


