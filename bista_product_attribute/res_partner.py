from openerp.osv import osv, fields
import time
from datetime import datetime, timedelta
from openerp.tools.float_utils import float_round as round
import openerp.addons.decimal_precision as dp
from openerp.osv.expression import get_unaccent_wrapper



class res_partner(osv.osv):
    _inherit= "res.partner"


    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            name = record.name
            if record.parent_id and not record.is_company:
                name =  "%s, %s" % (record.parent_id.name, name)
            if context.get('show_address'):
                name = name + "\n" + self._display_address(cr, uid, record, without_company=True, context=context)
                name = name.replace('\n\n','\n')
                name = name.replace('\n\n','\n')
            if context.get('show_email') and record.email:
                name = "%s <%s>" % (name, record.email)
            if record.x_client_id>0:
                print" calles new"
                name='[%d] %s'%(record.x_client_id,record.name)
            res.append((record.id, name))
        return res


    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if name and operator in ('=', 'ilike', '=ilike', 'like', '=like'):

            self.check_access_rights(cr, uid, 'read')
            where_query = self._where_calc(cr, uid, args, context=context)
            self._apply_ir_rules(cr, uid, where_query, 'read', context=context)
            from_clause, where_clause, where_clause_params = where_query.get_sql()
            where_str = where_clause and (" WHERE %s AND " % where_clause) or ' WHERE '

            # search on the name of the contacts and of its company
            search_name = name
            if operator in ('ilike', 'like'):
                search_name = '%%%s%%' % name
            if operator in ('=ilike', '=like'):
                operator = operator[1:]

            unaccent = get_unaccent_wrapper(cr)

            # TODO: simplify this in trunk with `display_name`, once it is stored
            # Perf note: a CTE expression (WITH ...) seems to have an even higher cost
            #            than this query with duplicated CASE expressions. The bulk of
            #            the cost is the ORDER BY, and it is inevitable if we want
            #            relevant results for the next step, otherwise we'd return
            #            a random selection of `limit` results.

            display_name = """CASE WHEN company.id IS NULL OR res_partner.is_company
                                   THEN {partner_name}
                                   ELSE {company_name} || ', ' || {partner_name}
                               END""".format(partner_name=unaccent('res_partner.name'),
                                             company_name=unaccent('company.name'))

            query = """SELECT res_partner.id
                         FROM res_partner
                    LEFT JOIN res_partner company
                           ON res_partner.parent_id = company.id
                      {where} ({email} {operator} {percent}
                           OR {display_name} {operator} {percent})
                     ORDER BY {display_name}
                    """.format(where=where_str, operator=operator,
                               email=unaccent('res_partner.email'),
                               percent=unaccent('%s'),
                               display_name=display_name)

            where_clause_params += [search_name, search_name]
            if limit:
                query += ' limit %s'
                where_clause_params.append(limit)
            cr.execute(query, where_clause_params)
            ids = map(lambda x: x[0], cr.fetchall())

            if ids:
                return self.name_get(cr, uid, ids, context)
            else:
                return []
        return super(res_partner,self).name_search(cr, uid, name, args, operator=operator, context=context, limit=limit)





    _columns={
        'x_vendor_id':fields.char('Vendor Id', size=128),
        'x_ein': fields.char('Employer Identification No',size=128),
        'x_street_3': fields.char('Street 3', size=128),

        'x_is_billing_vendor':fields.boolean('Is Billing Vendor'),
        'x_quote_terms':fields.text('Quote Terms'),
    }

res_partner()