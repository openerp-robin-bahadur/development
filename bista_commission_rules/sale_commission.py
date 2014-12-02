from osv import osv, fields
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
#from openerp.tools.safe_eval import safe_eval as eval
from datetime import datetime, timedelta
from math import ceil, floor

class sale_order(osv.osv):
    _inherit = 'sale.order'

    def _cal_commission_logic(self, cr, uid, rule_data, line_id,type):
        try:
            commission_value1 = 0.0
            commission_value2 = 0.0
            commission_value3 = 0.0
            exp = ['-','+','*','/','(',')']
            logical_exp=['<','>','!=','==','<=','>=']
            comm_obj = self.pool.get('commission.rules')
            result  = 0.0
            rule_field = []
            new_fld = []
            total_amount = {}
            for rd in rule_data:
                condition_field_old=rd['condition_one']
                condition_field=rd['condition_one']
                rule_old = rd['rule_one']
                rule_field = rd['rule_one']

                condition2_field_old=rd['condition_two']
                condition2_field=rd['condition_two']
                rule2_old=rd['rule_two']
                rule2_field=rd['rule_two']

                condition3_field_old=rd['condition_three']
                condition3_field=rd['condition_three']
                rule3_field=rd['rule_three']
                rule3_old=rd['rule_three']

                condition4_field_old=rd['condition_four']
                condition4_field=rd['condition_four']
                rule4_field=rd['rule_four']
                rule4_old=rd['rule_four']

                condition5_field_old=rd['condition_five']
                condition5_field=rd['condition_five']
                rule5_field=rd['rule_five']
                rule5_old=rd['rule_five']

                condition6_field_old=rd['condition_six']
                condition6_field=rd['condition_six']
                rule6_field=rd['rule_six']
                rule6_old=rd['rule_six']

    #                         ====condition one evaluation==
            if condition_field_old:
                for con in logical_exp:
                    condition_field = condition_field.replace(str(con),',')
                condition_field = condition_field.split(',')
            if condition_field and len(condition_field) > 1:
                for cld in condition_field:
                    if cld and len(cld.strip()) != 0:
                      new_fld.append(str(cld.strip()))

    #                           =====rule one evaluation====
            for ex in exp:
                rule_field = rule_field.replace(str(ex),',')
            rule_field = rule_field.split(',')
            if rule_field and len(rule_field) > 1:
                for fld in rule_field:
                    if fld and len(fld.strip()) != 0:
                      new_fld.append(str(fld.strip()))

    #                        === condition two evaluation===
            if condition2_field_old:
                for con in logical_exp:
                    condition2_field = condition2_field.replace(str(con),',')
                condition2_field = condition2_field.split(',')
            if condition2_field and len(condition2_field) > 1:
                for cld in condition2_field:
                    if cld and len(cld.strip()) != 0:
                      new_fld.append(str(cld.strip()))

    #                        =====rule two evaluation====
            if rule2_field:
                for ex in exp:
                    rule2_field = rule2_field.replace(str(ex),',')
                rule2_field = rule2_field.split(',')
            if rule2_field and len(rule2_field) > 1:
                for fld in rule2_field:
                    if fld and len(fld.strip()) != 0:
                      new_fld.append(str(fld.strip()))

    #                        =====condition three evalaution====
            if condition3_field_old:
                for con in logical_exp:
                    condition3_field = condition3_field.replace(str(con),',')
                condition3_field = condition3_field.split(',')
            if condition3_field and len(condition3_field) > 1:
                for cld in condition3_field:
                    if cld and len(cld.strip()) != 0:
                      new_fld.append(str(cld.strip()))

    #                        =======rule three evaluation======
            if rule3_field:
                for ex in exp:
                    rule3_field = rule3_field.replace(str(ex),',')
                rule3_field = rule3_field.split(',')
            if rule3_field and len(rule3_field) > 1:
                for fld in rule3_field:
                    if fld and len(fld.strip()) != 0:
                      new_fld.append(str(fld.strip()))

    #                        ====condition four evaluation====
            if condition4_field_old:
                for con in logical_exp:
                    condition4_field = condition4_field.replace(str(con),',')
                condition4_field = condition4_field.split(',')
            if condition4_field and len(condition4_field) > 1:
                for cld in condition4_field:
                    if cld and len(cld.strip()) != 0:
                      new_fld.append(str(cld.strip()))

    #                        =====rule four evaluation=====
            if rule4_field:
                for ex in exp:
                    rule4_field = rule4_field.replace(str(ex),',')
                rule4_field = rule4_field.split(',')
            if rule4_field and len(rule4_field) > 1:
                for fld in rule4_field:
                    if fld and len(fld.strip()) != 0:
                      new_fld.append(str(fld.strip()))

    #                       ==========condition five evaluation=======
            if condition5_field_old:
                for con in logical_exp:
                    condition5_field = condition5_field.replace(str(con),',')
                condition5_field = condition5_field.split(',')
            if condition5_field and len(condition5_field) > 1:
                for cld in condition5_field:
                    if cld and len(cld.strip()) != 0:
                      new_fld.append(str(cld.strip()))

    #                       =======rule five evaluation======
            if rule5_field:
                for ex in exp:
                    rule5_field = rule5_field.replace(str(ex),',')
                rule5_field = rule5_field.split(',')
            if rule5_field and len(rule5_field) > 1:
                for fld in rule5_field:
                    if fld and len(fld.strip()) != 0:
                      new_fld.append(str(fld.strip()))

    #                        ======condition six evaluation===

            if condition6_field_old:
                for con in logical_exp:
                    condition6_field = condition6_field.replace(str(con),',')
                condition6_field = condition6_field.split(',')
            if condition6_field and len(condition6_field) > 1:
                for cld in condition6_field:
                    if cld and len(cld.strip()) != 0:
                      new_fld.append(str(cld.strip()))

    #                        ======rule six evaluation====
            if rule6_field:
                for ex in exp:
                    rule6_field = rule6_field.replace(str(ex),',')
                rule6_field = rule6_field.split(',')
            if rule6_field and len(rule6_field) > 1:
                for fld in rule6_field:
                    if fld and len(fld.strip()) != 0:
                      new_fld.append(str(fld.strip()))

            read_field=self.pool.get('sale.order.line').read(cr,uid,line_id.id,new_fld)
            for key, value in read_field.iteritems():
                rule_old = rule_old.replace(str(key),str(value))
                if condition_field_old:
                    condition_field_old=condition_field_old.replace(str(key),str(value))

    #                            ====execution of condition2===
                if condition2_field_old:
                    condition2_field_old=condition2_field_old.replace(str(key),str(value))

    #                             =====execution of rule2 commission===
                if rule2_field:
                    rule2_old=rule2_old.replace(str(key),str(value))

    #                            ====execution of condition3===
                if condition3_field_old:
                    condition3_field_old=condition3_field_old.replace(str(key),str(value))

    #                            ======execution of rule3 commission===
                if rule3_field:
                    rule3_old=rule3_old.replace(str(key),str(value))
                   
    #                            ==== execution of condition4===
                if condition4_field_old:
                    condition4_field_old=condition4_field_old.replace(str(key),str(value))

    #                        =========execution of rule 4 commission========                                if rule4_field:
                    rule4_old=rule4_old.replace(str(key),str(value))

    #                          =======execution of condition5====
                if condition5_field_old:
                    condition5_field_old=condition5_field_old.replace(str(key),str(value))

    #                        =======execution of rule 5 commission
                if rule5_field:
                    rule5_old=rule5_old.replace(str(key),str(value))
    #                           ===== execution of condition6====
                if condition6_field_old:
                    condition6_field_old=condition6_field_old.replace(str(key),str(value))

    #                            ======ecxecution of rule 6 commission===

                if rule6_field:
                    rule6_old=rule6_old.replace(str(key),str(value))
    #                        evaluation of rule1 field
            if condition_field_old:
                if rule_old and eval(condition_field_old):
                    rule1=eval(rule_old)
                    result = rule1
            else:
                 if rule_old:
                    rule1=eval(rule_old)
                    result = rule1

    #                        evaluation of rule2 field
            if condition2_field_old:
                if 'rule1' in condition2_field_old:
                    condition2_field_old= condition2_field_old.replace('rule1',str(rule1))
                if rule2_old and eval(condition2_field_old):
                    if 'rule1' in rule2_old:
                        rule2_old= rule2_old.replace('rule1',str(rule1))
                    rule2=eval(rule2_old)
                    result = rule2
            else:
                 if rule2_old:
                    if 'rule1' in rule2_old:
                        rule2_old= rule2_old.replace('rule1',str(rule1))
                    rule2=eval(rule2_old)
                    result = rule2

    #                                evaluation rule3 field
            if condition3_field_old:
                if 'rule1' in condition3_field_old:
                    condition3_field_old= condition3_field_old.replace('rule1',str(rule1))
                if 'rule2' in condition3_field_old:
                    condition3_field_old= condition3_field_old.replace('rule2',str(rule2))
                if rule3_old and eval(condition3_field_old):
                    if 'rule1' in rule3_old:
                        rule3_old= rule3_old.replace('rule1',str(rule1))
                    if 'rule2' in rule3_old:
                        rule3_old= rule3_old.replace('rule2',str(rule2))
                    rule3=eval(rule3_old)
                    result = rule3
            else:
                 if rule3_old:
                    if 'rule1' in rule3_old:
                        rule3_old= rule3_old.replace('rule1',str(rule1))
                    if 'rule2' in rule3_old:
                        rule3_old= rule3_old.replace('rule2',str(rule2))
                    rule3=eval(rule3_old)
                    result = rule3

    #                                evaluation of rule4 field
            if condition4_field_old:
                if 'rule1' in condition4_field_old:
                    condition4_field_old= condition4_field_old.replace('rule1',str(rule1))
                if 'rule2' in condition4_field_old:
                    condition4_field_old= condition4_field_old.replace('rule2',str(rule2))
                if 'rule3' in condition4_field_old:
                    condition4_field_old= condition4_field_old.replace('rule3',str(rule3))
                if rule4_old and eval(condition4_field_old):
                    if 'rule1' in rule4_old:
                        rule4_old= rule4_old.replace('rule1',str(rule1))
                    if 'rule2' in rule4_old:
                        rule4_old = rule4_old.replace('rule2',str(rule2))
                    if 'rule3' in rule4_old:
                        rule4_old = rule4_old.replace('rule3',str(rule3))
                    rule4=eval(rule4_old)
                    result = rule4
            else:
                if rule4_old:
                    if 'rule1' in rule4_old:
                        rule4_old= rule4_old.replace('rule1',str(rule1))
                    if 'rule2' in rule4_old:
                        rule4_old = rule4_old.replace('rule2',str(rule2))
                    if 'rule3' in rule4_old:
                        rule4_old = rule4_old.replace('rule3',str(rule3))
                    rule4=eval(rule4_old)
                    result = rule4

    #                                   evalaution of rule5 field
            if condition5_field_old:
                if 'rule1' in condition5_field_old:
                    condition5_field_old = condition5_field_old.replace('rule1',str(rule1))
                if 'rule2' in condition5_field_old:
                    condition5_field_old = condition5_field_old.replace('rule2',str(rule2))
                if 'rule3' in condition5_field_old:
                    condition5_field_old = condition5_field_old.replace('rule3',str(rule3))
                if 'rule4' in condition5_field_old:
                    condition5_field_old = condition5_field_old.replace('rule4',str(rule4))
                if rule5_old and eval(condition5_field_old):
                    if 'rule1' in rule5_old:
                        rule5_old= rule5_old.replace('rule1',str(rule1))
                    if 'rule2' in rule5_old:
                        rule5_old = rule5_old.replace('rule2',str(rule2))
                    if 'rule3' in rule5_old:
                        rule5_old = rule5_old.replace('rule3',str(rule3))
                    if 'rule4' in rule5_old:
                        rule5_old = rule5_old.replace('rule4',str(rule4))
                    rule5=eval(rule5_old)
                    result = rule5
            else:
                 if rule5_old:
                    if 'rule1' in rule5_old:
                        rule5_old= rule5_old.replace('rule1',str(rule1))
                    if 'rule2' in rule5_old:
                        rule5_old = rule5_old.replace('rule2',str(rule2))
                    if 'rule3' in rule5_old:
                        rule5_old = rule5_old.replace('rule3',str(rule3))
                    if 'rule4' in rule5_old:
                        rule5_old = rule5_old.replace('rule4',str(rule4))
                    rule5=eval(rule5_old)
                    result = rule5
    #                                evaluation of rule6 field
            if condition6_field_old:
                if 'rule1' in condition6_field_old:
                    condition6_field_old = condition6_field_old.replace('rule1',str(rule1))
                if 'rule2' in condition6_field_old:
                    condition6_field_old = condition6_field_old.replace('rule2',str(rule2))
                if 'rule3' in condition6_field_old:
                    condition6_field_old = condition6_field_old.replace('rule3',str(rule3))
                if 'rule4' in condition6_field_old:
                    condition6_field_old = condition6_field_old.replace('rule4',str(rule4))
                if 'rule5' in condition6_field_old:
                    condition6_field_old = condition6_field_old.replace('rule5',str(rule5))
                if rule6_old and eval(condition6_field_old):
                    if 'rule1' in rule6_old:
                        rule6_old= rule6_old.replace('rule1',str(rule1))
                    if 'rule2' in rule6_old:
                        rule6_old = rule6_old.replace('rule2',str(rule2))
                    if 'rule3' in rule6_old:
                        rule6_old = rule6_old.replace('rule3',str(rule3))
                    if 'rule4' in rule6_old:
                        rule6_old = rule6_old.replace('rule4',str(rule4))
                    if 'rule5' in rule6_old:
                        rule6_old = rule6_old.replace('rule5',str(rule5))
                    rule6=eval(rule6_old)
                    result = rule6
            else:
                 if rule6_old:
                    if 'rule1' in rule6_old:
                        rule6_old= rule6_old.replace('rule1',str(rule1))
                    if 'rule2' in rule6_old:
                        rule6_old = rule6_old.replace('rule2',str(rule2))
                    if 'rule3' in rule6_old:
                        rule6_old = rule6_old.replace('rule3',str(rule3))
                    if 'rule4' in rule6_old:
                        rule6_old = rule6_old.replace('rule4',str(rule4))
                    if 'rule5' in rule6_old:
                        rule6_old = rule6_old.replace('rule5',str(rule5))
                    rule6=eval(rule6_old)
                    result = rule6
            if result:
                if type=='territory':
                    if line_id.order_id.territory_manager1_commission:
                        commission_value1 += (line_id.order_id.territory_manager1_commission / 100.00)*result
                    if line_id.order_id.territory_manager2_commission:
                        commission_value2 += (line_id.order_id.territory_manager2_commission / 100.00)*result
                    if line_id.order_id.territory_manager3_commission:
                        commission_value3 += (line_id.order_id.territory_manager3_commission / 100.00)*result
                if type=='regional':
                    if line_id.order_id.regional_manager1_commission:
                        commission_value1 += (line_id.order_id.regional_manager1_commission / 100.00)*result
                    if line_id.order_id.regional_manager2_commission:
                        commission_value2 += (line_id.order_id.regional_manager2_commission / 100.00)*result
                    if line_id.order_id.regional_manager3_commission:
                        commission_value3 += (line_id.order_id.regional_manager3_commission / 100.00)*result
                if type=='brand':
                    if line_id.order_id.brand_manager1_commission:
                        commission_value1 += (line_id.order_id.brand_manager1_commission / 100.00)*result
                    if line_id.order_id.brand_manager2_commission:
                        commission_value2 += (line_id.order_id.brand_manager2_commission / 100.00)*result
                    if line_id.order_id.brand_manager3_commission:
                        commission_value3 += (line_id.order_id.brand_manager3_commission / 100.00)*result
                   
            total_amount['result1'] = commission_value1
            total_amount['result2'] = commission_value2
            total_amount['result3'] = commission_value3
            return total_amount
        except:
            raise osv.except_osv(_('Error!'),
                _('Commission cannot be calculated \n Please check the Commission Rules'))


    def run_commission(self, cr, uid, ids, context=None):
        type=False
        for each in self.browse(cr,uid,ids):
            if (each.territory_manager1_id and not each.territory_manager2_id) and each.territory_manager3_id:
                raise osv.except_osv(_('Error!'),
                _(' Territory Manager 3 Cannot be selected without Manager 2'))
            if not each.territory_manager1_id and (each.territory_manager2_id or each.territory_manager3_id):
                raise osv.except_osv(_('Error!'),
                _('Manager 2 and Manager 3 Cannot be selected without Manager 1'))
            

            else:
                if each.territory_manager1_commission>0 and each.territory_manager2_commission>0 and each.territory_manager3_commission>0:
                    if (each.territory_manager2_commission and each.territory_manager3_commission) and(not each.territory_manager2_id or not each.territory_manager3_id):
                        raise osv.except_osv(_('Error!'),
                            _('Please Select Territory Manager \n before defining the commission rate '))
                    total=each.territory_manager1_commission+each.territory_manager2_commission+each.territory_manager3_commission
                    if total != 100:
                         raise osv.except_osv(_('Error!'),
                            _('Total Commission for the Managers are invalid \n should be sum up to 100 '))
                elif each.territory_manager1_commission>0 and each.territory_manager2_commission>0:
                    if not each.territory_manager2_id:
                        raise osv.except_osv(_('Error!'),
                            _('Please Select Territory Manager \n before defining the commission rate '))
                    total=each.territory_manager1_commission+each.territory_manager2_commission
                    if total != 100:
                         raise osv.except_osv(_('Error!'),
                            _('Total Commission for the two Managers are invalid \n should be sum up to 100 '))
                elif each.territory_manager1_commission>0 and each.territory_manager3_commission>0:
                    if each.territory_manager2_id and each.territory_manager2_commission<=0:
                        raise osv.except_osv(_('Error!'),
                            _('Please Select rate for territory manager 2 or \n rate for the Manager should be greater than Zero'))

                    if not each.territory_manager3_id:
                        raise osv.except_osv(_('Error!'),
                            _('Please Select Territory Manager \n before defining the commission rate '))
                    total=each.territory_manager1_commission+each.territory_manager3_commission
                    if total != 100:
                         raise osv.except_osv(_('Error!'),
                            _('Total Commission for the two Managers are invalid \n should be sum up to 100 '))

                elif each.territory_manager1_commission != 100:
                     raise osv.except_osv(_('Error!'),
                            _('Total Commission for the one Manager is invalid \n should be sum up to 100 '))
                else:
                    pass

#                    =========calculation for the Reigional manager==========

            if (each.regional_manager1_id and not each.regional_manager2_id) and each.regional_manager3_id:
                raise osv.except_osv(_('Error!'),
                _(' Regional Manager 3 Cannot be selected without Manager 2'))

            if not each.regional_manager1_id and (each.regional_manager2_id or each.regional_manager3_id):
                raise osv.except_osv(_('Error!'),
                _('Regional Manager 2 and  Regional Manager 3 Cannot be selected without \n Regional Manager 1'))
            

            else:
                if each.regional_manager1_commission>0 and each.regional_manager2_commission>0 and each.regional_manager3_commission>0:
                    if (each.regional_manager2_commission and each.regional_manager3_commission) and(not each.regional_manager2_id or not each.regional_manager3_id):
                        raise osv.except_osv(_('Error!'),
                            _('Please Select Regional Manager \n before defining the commission rate '))
                    total=each.regional_manager1_commission+each.regional_manager2_commission+each.regional_manager3_commission
                    if total != 100:
                         raise osv.except_osv(_('Error!'),
                            _('Total Commission for the Regional Managers are invalid \n should be sum up to 100 '))
                elif each.regional_manager1_commission>0 and each.regional_manager2_commission>0:
                    if not each.regional_manager2_id:
                        raise osv.except_osv(_('Error!'),
                            _('Please Select Regional Manager \n before defining the commission rate '))
                    total=each.regional_manager1_commission+each.regional_manager2_commission
                    if total != 100:
                         raise osv.except_osv(_('Error!'),
                            _('Total Commission for the two Regional Managers are invalid \n should be sum up to 100 '))
                elif each.regional_manager1_commission>0 and each.regional_manager3_commission>0:
                    if not each.regional_manager3_id:
                        raise osv.except_osv(_('Error!'),
                            _('Please Select Regional Manager \n before defining the commission rate '))
                    if each.regional_manager2_id and each.regional_manager2_commission<=0:
                        raise osv.except_osv(_('Error!'),
                            _('Please Select rate for Regional Manager 2 or \n rate for the Manager should be greater than Zero'))
                    total=each.territory_manager1_commission+each.territory_manager3_commission
                    if total != 100:
                         raise osv.except_osv(_('Error!'),
                            _('Total Commission for the two Regional Managers are invalid \n should be sum up to 100 '))
                
                elif each.regional_manager1_id and each.regional_manager1_commission != 100:
                     raise osv.except_osv(_('Error!'),
                            _('Total Commission for the one Regional Managers are invalid \n should be sum up to 100 '))
                else:
                    pass

#                    =====Commission calculation for the Brand manager======

            if (each.brand_manager1_id and not each.brand_manager2_id) and each.brand_manager3_id:
                raise osv.except_osv(_('Error!'),
                _(' Brand Manager 3 Cannot be selected without Manager 2'))
            if not each.brand_manager1_id and (each.brand_manager2_id or each.brand_manager3_id):
                raise osv.except_osv(_('Error!'),
                _('Brand Manager 2 and  Brand Manager 3 Cannot be selected without \n Brand Manager 1'))
            

            else:
                if each.brand_manager1_commission>0 and each.brand_manager2_commission>0 and each.brand_manager3_commission>0:
                    if (each.brand_manager2_commission and each.brand_manager3_commission) and(not each.brand_manager2_id or not each.brand_manager3_id):
                        raise osv.except_osv(_('Error!'),
                            _('Please Select Brand Manager \n before defining the commission rate '))
                    total=each.brand_manager1_commission+each.brand_manager2_commission+each.brand_manager3_commission
                    if total != 100:
                         raise osv.except_osv(_('Error!'),
                            _('Total Commission for the Brand Managers are invalid \n should be sum up to 100 '))
                elif each.brand_manager1_commission>0 and each.brand_manager2_commission>0:
                    if not each.brand_manager2_id:
                        raise osv.except_osv(_('Error!'),
                            _('Please Select Brand Manager \n before defining the commission rate '))
                    total=each.brand_manager1_commission+each.brand_manager2_commission
                    if total != 100:
                         raise osv.except_osv(_('Error!'),
                            _('Total Commission for the two Brand Managers are invalid \n should be sum up to 100 '))

                elif each.brand_manager1_commission>0 and each.brand_manager3_commission>0:
                    if not each.brand_manager3_id:
                        raise osv.except_osv(_('Error!'),
                            _('Please Select Brand Manager \n before defining the commission rate '))
                    if each.brand_manager2_id and each.brand_manager2_commission<=0:
                        raise osv.except_osv(_('Error!'),
                            _('Please Select rate for Brand Manager 2 or \n rate for the Manager should be greater than Zero'))
                    total=each.brand_manager1_commission+each.brand_manager3_commission
                    if total != 100:
                         raise osv.except_osv(_('Error!'),
                            _('Total Commission for the two Brand Managers are invalid \n should be sum up to 100 '))
                elif  each.brand_manager1_id and each.brand_manager1_commission != 100:
                     raise osv.except_osv(_('Error!'),
                            _('Total Commission for the one Brand Managers are invalid \n should be sum up to 100 '))
                else:
                    pass

            commission_value1 = 0.0
            commission_value2 = 0.0
            commission_value3 = 0.0
            for line in each.order_line:
                if line.product_id and each.territory_manager1_id and each.territory_manager1_id.job_id:
                    rule_id=self.pool.get('commission.rules').search(cr,uid,[('designation_id.id','=',each.territory_manager1_id.job_id.id),('product_id.id','=',line.product_id.id)],limit=1,order='commission_date desc')
                    if not rule_id:
                        rule_id=self.pool.get('commission.rules').search(cr,uid,[('designation_id.id','=',each.territory_manager1_id.job_id.id),('product_id.id','=',line.product_id.id)],limit=1,order='commission_date')
                    if rule_id:
                        type='territory'
                        rule_data = self.pool.get('commission.rules').read(cr, uid, rule_id, ['condition_one','rule_one','condition_two','rule_two','condition_three','rule_three','condition_four','rule_four','condition_five','rule_five','condition_six','rule_six'])
                        comm_result = self._cal_commission_logic(cr, uid, rule_data, line,type)
                        commission_value1 += comm_result['result1']
                        commission_value2 += comm_result['result2']
                        commission_value3 += comm_result['result3']
            self.write(cr,uid,ids,{'territory_manager1_commission_val':commission_value1,'territory_manager2_commission_val':commission_value2,'territory_manager3_commission_val':commission_value3})
            regional_commission_value1 = 0.0
            regional_commission_value2 = 0.0
            regional_commission_value3 = 0.0
            for line in each.order_line:
                if line.product_id and each.regional_manager1_id and each.regional_manager1_id.job_id:
                    rule_id=self.pool.get('commission.rules').search(cr,uid,[('designation_id.id','=',each.regional_manager1_id.job_id.id),('product_id.id','=',line.product_id.id)],limit=1,order='commission_date desc')
                    print"rule_data for the Regionalcommssion rules",rule_id
                    if not rule_id:
                        rule_id=self.pool.get('commission.rules').search(cr,uid,[('designation_id.id','=',each.regional_manager1_id.job_id.id),('product_id.id','=',line.product_id.id)],limit=1,order='commission_date')
                    if rule_id:
                        type='regional'
                        rule_data = self.pool.get('commission.rules').read(cr, uid, rule_id, ['condition_one','rule_one','condition_two','rule_two','condition_three','rule_three','condition_four','rule_four','condition_five','rule_five','condition_six','rule_six'])
                        comm_result = self._cal_commission_logic(cr, uid, rule_data, line,type)
                        regional_commission_value1 += comm_result['result1']
                        regional_commission_value2 += comm_result['result2']
                        regional_commission_value3 += comm_result['result3']

            self.write(cr,uid,ids,{'regional_manager1_commission_val':regional_commission_value1,'regional_manager2_commission_val':regional_commission_value2,'regional_manager3_commission_val':regional_commission_value3})

            brand_commission_value1 = 0.0
            brand_commission_value2 = 0.0
            brand_commission_value3 = 0.0
            for line in each.order_line:
                if line.product_id and each.brand_manager1_id and each.brand_manager1_id.job_id:
                    rule_id=self.pool.get('commission.rules').search(cr,uid,[('designation_id.id','=',each.brand_manager1_id.job_id.id),('product_id.id','=',line.product_id.id)],limit=1,order='commission_date desc')
                    if not rule_id:
                        rule_id=self.pool.get('commission.rules').search(cr,uid,[('designation_id.id','=',each.brand_manager1_id.job_id.id),('product_id.id','=',line.product_id.id)],limit=1,order='commission_date')
                    if rule_id:
                        type='brand'
                        rule_data = self.pool.get('commission.rules').read(cr, uid, rule_id, ['condition_one','rule_one','condition_two','rule_two','condition_three','rule_three','condition_four','rule_four','condition_five','rule_five','condition_six','rule_six'])
                        comm_result = self._cal_commission_logic(cr, uid, rule_data, line,type)
                        brand_commission_value1 += comm_result['result1']
                        brand_commission_value2 += comm_result['result2']
                        brand_commission_value3 += comm_result['result3']

            self.write(cr,uid,ids,{'brand_manager1_commission_val':brand_commission_value1,'brand_manager2_commission_val':brand_commission_value2,'brand_manager3_commission_val':brand_commission_value3})

    def onchange_manager1_id(self, cr, uid, ids, territory_manager1_id, context=None):
       v = {}
       if territory_manager1_id:
            v['territory_manager1_commission']=False
            v['territory_manager1_commission_val']=False
       return {'value': v}

    def onchange_manager2_id(self, cr, uid, ids, territory_manager2_id, context=None):
       v = {}
       if territory_manager2_id:
            v['territory_manager2_commission']=False
            v['territory_manager2_commission_val']=False
       return {'value': v}

    def onchange_manager3_id(self, cr, uid, ids, territory_manager3_id, context=None):
       v = {}
       if territory_manager3_id:
            v['territory_manager3_commission']=False
            v['territory_manager3_commission_val']=False
       return {'value': v}


    def on_change_manager1_commission(self, cr, uid, ids, territory_manager1_commission, context=None):
        v={}
        if not territory_manager1_commission:
            v['territory_manager1_commission_val']=False
        return{'value':v}


    def on_change_manager2_commission(self, cr, uid, ids, territory_manager2_commission, context=None):
        v={}
        if not territory_manager2_commission:
            v['territory_manager2_commission_val']=False
        return{'value':v}


    def on_change_manager3_commission(self, cr, uid, ids, territory_manager3_commission, context=None):
        v={}
        if not territory_manager3_commission:
            v['territory_manager3_commission_val']=False
        return{'value':v}

#        ====onchange for the regional manager=====


    def onchange_regional_manager1_id(self, cr, uid, ids, regional_manager1_id, context=None):
       v = {}
       if regional_manager1_id:
            v['regional_manager1_commission']=False
            v['regional_manager1_commission_val']=False
       return {'value': v}

    def onchange_regional_manager2_id(self, cr, uid, ids, regional_manager2_id, context=None):
       v = {}
       if regional_manager2_id:
            v['regional_manager2_commission']=False
            v['regional_manager2_commission_val']=False
       return {'value': v}

    def onchange_regional_manager3_id(self, cr, uid, ids, regional_manager3_id, context=None):
       v = {}
       if regional_manager3_id:
            v['regional_manager3_commission']=False
            v['regional_manager3_commission_val']=False
       return {'value': v}


    def on_change_regional_manager1_commission(self, cr, uid, ids, regional_manager1_commission, context=None):
        v={}
        if not regional_manager1_commission:
            v['regional_manager1_commission_val']=False
        return{'value':v}


    def on_change_regional_manager2_commission(self, cr, uid, ids, regional_manager2_commission, context=None):
        v={}
        if not regional_manager2_commission:
            v['regional_manager2_commission_val']=False
        return{'value':v}


    def on_change_regional_manager3_commission(self, cr, uid, ids, regional_manager3_commission, context=None):
        v={}
        if not regional_manager3_commission:
            v['regional_manager3_commission_val']=False
        return{'value':v}

#            ======onchange for the Brand Manager=======


    def onchange_brand_manager1_id(self, cr, uid, ids, brand_manager1_id, context=None):
       v = {}
       if brand_manager1_id:
            v['brand_manager1_commission']=False
            v['brand_manager1_commission_val']=False
       return {'value': v}

    def onchange_brand_manager2_id(self, cr, uid, ids, brand_manager2_id, context=None):
       v = {}
       if brand_manager2_id:
            v['brand_manager2_commission']=False
            v['brand_manager2_commission_val']=False
       return {'value': v}

    def onchange_brand_manager3_id(self, cr, uid, ids, brand_manager3_id, context=None):
       v = {}
       if brand_manager3_id:
            v['brand_manager3_commission']=False
            v['brand_manager3_commission_val']=False
       return {'value': v}


    def on_change_brand_manager1_commission(self, cr, uid, ids, brand_manager1_commission, context=None):
        v={}
        if not brand_manager1_commission:
            v['brand_manager1_commission_val']=False
        return{'value':v}

    def on_change_brand_manager2_commission(self, cr, uid, ids, brand_manager2_commission, context=None):
        v={}
        if not brand_manager2_commission:
            v['brand_manager2_commission_val']=False
        return{'value':v}

    def on_change_brand_manager3_commission(self, cr, uid, ids, brand_manager3_commission, context=None):
        v={}
        if not brand_manager3_commission:
            v['brand_manager3_commission_val']=False
        return{'value':v}

    _columns = {
               
                'territory_manager1_id':fields.many2one('hr.employee','Sales Person 1',readonly=True),
                'territory_manager2_id':fields.many2one('hr.employee','Sales Person 2'),
                'territory_manager3_id':fields.many2one('hr.employee','Sales Person 3'),
                'regional_manager1_id':fields.many2one('hr.employee','Regional Manager 1'),
                'regional_manager2_id':fields.many2one('hr.employee','Regional Manager 2'),
                'regional_manager3_id':fields.many2one('hr.employee','Regional Manager 3'),
                'brand_manager1_id':fields.many2one('hr.employee','Brand Manager 1'),
                'brand_manager2_id':fields.many2one('hr.employee','Brand Manager 2'),
                'brand_manager3_id':fields.many2one('hr.employee','Brand Manager 3'),
                'territory_manager1_commission':fields.integer('Commision Rate'),
                'territory_manager2_commission':fields.integer('Commision Rate'),
                'territory_manager3_commission':fields.integer('Commision Rate'),
                'regional_manager1_commission':fields.integer('Commision Rate'),
                'regional_manager2_commission':fields.integer('Commision Rate'),
                'regional_manager3_commission':fields.integer('Commision Rate'),
                'brand_manager1_commission':fields.integer('Commision Rate'),
                'brand_manager2_commission':fields.integer('Commision Rate'),
                'brand_manager3_commission':fields.integer('Commision Rate'),
                'territory_manager1_commission_val':fields.float('Commision 1',readonly=True,digits_compute= dp.get_precision('Account')),
                'territory_manager2_commission_val':fields.float('Commision 2',readonly=True,digits_compute= dp.get_precision('Account')),
                'territory_manager3_commission_val':fields.float('Commision 3',readonly=True,digits_compute= dp.get_precision('Account')),
                'regional_manager1_commission_val':fields.float('Commision 1',readonly=True,digits_compute= dp.get_precision('Account')),
                'regional_manager2_commission_val':fields.float('Commision 2',readonly=True,digits_compute= dp.get_precision('Account')),
                'regional_manager3_commission_val':fields.float('Commision 3',readonly=True,digits_compute= dp.get_precision('Account')),
                'brand_manager1_commission_val':fields.float('Commision 1',readonly=True,digits_compute= dp.get_precision('Account')),
                'brand_manager2_commission_val':fields.float('Commision 2',readonly=True,digits_compute= dp.get_precision('Account')),
                'brand_manager3_commission_val':fields.float('Commision 3',readonly=True,digits_compute= dp.get_precision('Account')),
                'other_manager_id':fields.many2one('hr.employee','Other Manager'),
                }


    def create(self,cr,uid,vals,context=None):
        res=super(sale_order,self).create(cr, uid, vals, context)
        if vals.get('user_id'):
            sales_manger_id=self.pool.get('hr.employee').search(cr,uid,[('user_id.id','=',vals.get('user_id'))],limit=1)
            if not sales_manger_id:
                raise osv.except_osv(_('Error!'),
                _('Current user is not assign to any employee'))
            vals.update({'territory_manager1_id':sales_manger_id[0]})

        return res

    def write(self,cr,uid,ids,vals,context=None):
        sales_manger_id=[]
        res=super(sale_order,self).write(cr,uid,ids,vals,context)
        for each in self.browse(cr,uid,ids):
            if each.user_id:
                sales_manger_id=self.pool.get('hr.employee').search(cr,uid,[('user_id.id','=',each.user_id.id)],limit=1)
                if not sales_manger_id:
                    raise osv.except_osv(_('Error!'),
                    _('Current user is not assign to any employee'))
                res=super(sale_order,self).write(cr, uid,ids,{'territory_manager1_id':sales_manger_id[0]}, context)
            return res














        
