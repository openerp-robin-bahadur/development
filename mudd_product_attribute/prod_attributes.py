from openerp.osv import fields, osv
from datetime import datetim
from dateutil import parser

class template_size(osv.osv):
        _name= "template.size"
        _columns = {
            'name': fields.char('Size', size=100, required= True, help="Please enter Size"),
            }
template_size()


class template_paper(osv.osv):
        _name= "template.paper"
        _columns = {
            'name': fields.char('Paper Type', size=100, required= True, help="Please enter type of paper "),
            }
template_paper()

class template_color(osv.osv):
        _name= "template.color"
        _columns = {
            'name': fields.char('Color', size=100, required= True, help="Please enter Color"),
            }
template_color()

class template_fold(osv.osv):
        _name= "template.fold"
        _columns = {
            'name': fields.char('Folding Type', size=100, required= True, help="Please specify Folding type."),
            }
template_fold()

class template_envelope(osv.osv):
        _name= "template.envelope"
        _columns = {
            'name': fields.char('Envelope Type', size=100, required= True, help="Please specify type of Envelope."),
            }
template_envelope()

class template_postage(osv.osv):
        _name= "template.postage"
        _columns = {
            'name': fields.char('Postage', size=100, required= True),
            }
template_postage()

class template_postage_class(osv.osv):
        _name= "template.postage.class"
        _columns = {
            'name': fields.char('Envelope Type', size=100, required= True, help="Please specify type of Envelope."),
            }
template_postage_class()

class template_pop_out(osv.osv):
        _name= "template.pop.out"
        _columns = {
            'name': fields.char('Pop-Out Type', size=100, required= True, help="Please specify Pop-out type."),
            }
template_pop_out()

class template_note(osv.osv):
        _name= "template.note"
        _columns = {
            'name': fields.char('Sticky Note', size=100, required= True, help="Please specify type of Note."),
            }
template_note()





