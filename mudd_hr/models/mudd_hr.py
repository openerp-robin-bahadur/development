from osv import osv, fields
from datetime import date

class hr_employee(osv.Model):
	_inherit = "hr.employee"


	_columns = {
		'x_start_date': fields.date('Start Date'),
		'x_extension': fields.char('Ext', size=3),
		'x_fax': fields.char('Fax'),
		'x_birth_month': fields.char('Birth Month', size=2),
		'x_birth_day': fields.char('Birth Day', size=2),
	}

	def fields_view_get(self, cr, uid, view_id=None, view_type='tree', context=None, toolbar=False, submenu=False):
		res = super(hr_employee, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type,
			context=context, toolbar=toolbar, submenu=submenu)

		return res

	def ValidateBirthMonthAndDay(self, cr, uid, ids, birth_month=None, birth_day=None):
		if not birth_month and not birth_day:
			return True

		if not ids:
			if birth_month or birth_day:
				try:
				   	t = date(date.today().year, int(birth_month), int(birth_day))
				except:
				   	raise osv.except_osv('Invalid Birth Month / Birth Day Combination', 'Please Correct')
			return True
				
			

		# get the employee info
		employee = self.browse(cr, uid, ids[0])
		try:
		   	t = date(date.today().year, int(birth_month), int(birth_day))
		except:
		   	raise osv.except_osv('Invalid Birth Month / Birth Day Combination', 'Please Correct')
		return True
	
	def create(self, cr, uid,values,context=None):
		if 'x_birth_month' in values or 'x_birth_day' in values:
			birth_month = None
			birth_day = None
		   	if 'x_birth_month' in values:
				birth_month = values['x_birth_month']
		   	if 'x_birth_day' in values:
			  	birth_day = values['x_birth_day']
			
		   	self.ValidateBirthMonthAndDay(cr,uid,[],birth_month,birth_day)
		res = super(hr_employee, self).create(cr,uid,values,context=context)
		return res

	def write(self, cr, uid, ids, values, context=None):
		if 'x_birth_month' in values or 'x_birth_day' in values:
		   	birth_month = None
		   	birth_day = None
		   	if 'x_birth_month' in values:
				birth_month = values['x_birth_month']
		   	if 'x_birth_day' in values:
			  	birth_day = values['x_birth_day']
		   	self.ValidateBirthMonthAndDay(cr,uid,ids,birth_month,birth_day)
		res = super(hr_employee, self).write(cr, uid, ids, values, context=context)
		return res

