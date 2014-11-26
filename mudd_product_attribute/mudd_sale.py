from openerp.osv import fields, osv
from openerp.tools.translate import _
from lxml import etree
from tools.translate import translate


class sale_order(osv.osv):
    _inherit = "sale.order"
    

    _columns = {
        'product_temp_id':fields.many2one('product.template','Product Template'),
        'mudd_product_id':fields.many2one('product.product','Product'),
    }

   


sale_order()
