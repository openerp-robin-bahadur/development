import time

from openerp.report import report_sxw

class sale_report_hypercasting(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(sale_report_hypercasting, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
        })

#1.name desc in xml 2.object name 3. path 4.parser for current task 5.header which is optional

report_sxw.report_sxw('report.hypercasting.sale.order', 'sale.order', 'addons/quoteflow/report/sale_hypercasting.rml', parser=sale_report_hypercasting, header="external")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

