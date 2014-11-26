import time

from openerp.report import report_sxw
from osv import osv, fields
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
from dateutil.relativedelta import relativedelta
import pytz
from openerp import pooler, tools
#from netsvc import Service
#del Service._services['report.sale.order']

class quotation_sale_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(quotation_sale_report, self).__init__(cr, uid, name, context=context)
        self.localcontext .update({
            'time': time,
            'get_date':self.get_date,
        })

    def get_date(self,context=None):
        tz_name = pooler.get_pool(self.cr.dbname).get('res.users').read(self.cr, self.uid, self.uid, ['tz'])['tz']
        if not tz_name:
            tz_name = 'America/Chicago'
        user_datetime = datetime.strptime(datetime.today().strftime('%Y-%m-%d %H:%M:%S'), DEFAULT_SERVER_DATETIME_FORMAT)
        dt=datetime.today().strftime('%Y-%m-%d %H:%M:%S %p')
        dts=datetime.strptime(dt,'%Y-%m-%d %H:%M:%S %p')
        if tz_name:
            utc = pytz.timezone('UTC')
            context_tz = pytz.timezone(tz_name)
            user_datetime = dts - relativedelta(hours=9.0)
            local_timestamp = context_tz.localize(user_datetime, is_dst=False)
            user_datetime = local_timestamp.astimezone(utc)
            user_datetime=user_datetime-timedelta(hours=1)
        return user_datetime.strftime('%m/%d/%Y %I:%M:%S %p')

#1.name desc in xml 2.object name 3. path 4.parser for current task 5.header which is optional

report_sxw.report_sxw('report.quotation.sale.order', 'sale.order', 'addons/quoteflow/report/sale_order.rml', parser=quotation_sale_report, header="external")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

#class sale_report_gm(report_sxw.rml_parse):
#    def __init__(self, cr, uid, name, context=None):
#        super(sale_report_gm, self).__init__(cr, uid, name, context=context)
#        self.localcontext.update({
#            'time': time,
#        })

#1.name desc in xml 2.object name 3. path 4.parser for current task 5.header which is optional

#report_sxw.report_sxw('report.mudd.sale.order.gm', 'sale.order', 'addons/quoteflow/report/report_gm.rml', parser=sale_report_gm,header="external")



#class sale_report_market_center(report_sxw.rml_parse):
#    def __init__(self, cr, uid, name, context=None):
#        super(sale_report_market_center, self).__init__(cr, uid, name, context=context)
#        self.localcontext.update({
#            'time': time,
#        })
#
##1.name desc in xml 2.object name 3. path 4.parser for current task 5.header which is optional
#
#report_sxw.report_sxw('report.mudd.sale.order.market.center', 'sale.order', 'addons/quoteflow/report/report_market.rml', parser=sale_report_market_center,header="external")
class quotation_sale_report2(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(quotation_sale_report2, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_date':self.get_date,
            })

    def get_date(self,context=None):
        tz_name = pooler.get_pool(self.cr.dbname).get('res.users').read(self.cr, self.uid, self.uid, ['tz'])['tz']
        if not tz_name:
            tz_name = 'America/Chicago'
        user_datetime = datetime.strptime(datetime.today().strftime('%Y-%m-%d %H:%M:%S'), DEFAULT_SERVER_DATETIME_FORMAT)
        dt=datetime.today().strftime('%Y-%m-%d %H:%M:%S %p')
        dts=datetime.strptime(dt,'%Y-%m-%d %H:%M:%S %p')
        if tz_name:
            utc = pytz.timezone('UTC')
            context_tz = pytz.timezone(tz_name)
            user_datetime = dts - relativedelta(hours=9.0)
            local_timestamp = context_tz.localize(user_datetime, is_dst=False)
            user_datetime = local_timestamp.astimezone(utc)
            user_datetime=user_datetime-timedelta(hours=1)
        return user_datetime.strftime('%m/%d/%Y %I:%M:%S %p')
        
report_sxw.report_sxw('report.quotation.sale.order2', 'sale.order', 'addons/quoteflow/report/sale_order2.rml', parser=quotation_sale_report2, header="external")