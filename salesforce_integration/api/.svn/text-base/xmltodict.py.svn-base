from xml.parsers import expat
from xml.sax.saxutils import XMLGenerator
from xml.sax.xmlreader import AttributesImpl
from xml.dom.minidom import Document
try: #
    from cStringIO import StringIO
except ImportError: # pragma no cover
    try:
        from StringIO import StringIO
    except ImportError:
        from io import StringIO
try: 
    from collections import OrderedDict
except ImportError: 
    try: 
        from ordereddict import OrderedDict
    except ImportError:
        OrderedDict = dict

try:
    _basestring = basestring
except NameError: 
    _basestring = str
try:
    _unicode = unicode
except NameError: 
    _unicode = str



class ParsingInterrupted(Exception): pass

class _DictSAXHandler(object):
    def __init__(self,
                 item_depth=0,
                 item_callback=lambda *args: True,
                 xml_attribs=True,
                 attr_prefix='@',
                 cdata_key='text',
                 force_cdata=False,
                 cdata_separator='',
                 postprocessor=None,
                 dict_constructor=OrderedDict,
                 strip_whitespace=True):
        self.path = []
        self.stack = []
        self.data = None
        self.item = None
        self.item_depth = item_depth
        self.xml_attribs = xml_attribs
        self.item_callback = item_callback
        self.attr_prefix = attr_prefix
        self.cdata_key = cdata_key
        self.force_cdata = force_cdata
        self.cdata_separator = cdata_separator
        self.postprocessor = postprocessor
        self.dict_constructor = dict_constructor
        self.strip_whitespace = strip_whitespace

    def startElement(self, name, attrs):
        attrs = self.dict_constructor(zip(attrs[0::2], attrs[1::2]))
        self.path.append((name, attrs or None))
        if len(self.path) > self.item_depth:
            self.stack.append((self.item, self.data))
            if self.xml_attribs:
                attrs = self.dict_constructor(
                    (self.attr_prefix+key, value)
                    for (key, value) in attrs.items())
            else:
                attrs = None
            self.item = attrs or None
            self.data = None

    def endElement(self, name):
        if len(self.path) == self.item_depth:
            item = self.item
            if item is None:
                item = self.data
            should_continue = self.item_callback(self.path, item)
            if not should_continue:
                raise ParsingInterrupted()
        if len(self.stack):
            item, data = self.item, self.data
            self.item, self.data = self.stack.pop()
            if self.strip_whitespace and data is not None:
                data = data.strip() or None
            if data and self.force_cdata and item is None:
                item = self.dict_constructor()
            if item is not None:
                if data:
                    self.push_data(item, self.cdata_key, data)
                self.item = self.push_data(self.item, name, item)
            else:
                self.item = self.push_data(self.item, name, data)
        else:
            self.item = self.data = None
        self.path.pop()

    def characters(self, data):
        if not self.data:
            self.data = data
        else:
            self.data += self.cdata_separator + data

    def push_data(self, item, key, data):
        if self.postprocessor is not None:
            result = self.postprocessor(self.path, key, data)
            if result is None:
                return item
            key, data = result
        if item is None:
            item = self.dict_constructor()
        try:
            value = item[key]
            if isinstance(value, list):
                value.append(data)
            else:
                item[key] = [value, data]
        except KeyError:
            item[key] = data
        return item
        
#Parse the given XML input and convert it into a dictionary.
def parse(xml_input, encoding='utf-8', expat=expat, *args, **kwargs):


    handler = _DictSAXHandler(*args, **kwargs)
    parser = expat.ParserCreate()
    parser.ordered_attributes = True
    parser.StartElementHandler = handler.startElement
    parser.EndElementHandler = handler.endElement
    parser.CharacterDataHandler = handler.characters
    try:
        parser.ParseFile(xml_input)
    except (TypeError, AttributeError):
        if isinstance(xml_input, _unicode):
            xml_input = xml_input.encode(encoding)
        parser.Parse(xml_input, True)
    return handler.item

# This function convert the given Python dict in to corresponding xml 
def dict2xml(structure,xmlns={}):
     doc     = Document()
     rootName    = str(structure.keys()[0])
     root   = doc.createElement(rootName)
     for key,val in xmlns.iteritems():
           root.setAttribute(key,val)
    
     
     doc.appendChild(root)

     def build(father, structure):
        if type(structure) == dict:
            for k in structure:
                tag = doc.createElement(k)
                father.appendChild(tag)
                build(tag, structure[k])

        elif type(structure) == list:
            grandFather = father.parentNode
            tagName     = father.tagName
            grandFather.removeChild(father)
            for l in structure:
                tag = doc.createElement(tagName)
                build(tag, l)
                grandFather.appendChild(tag)

        else:
            data    = str(structure)
            tag     = doc.createTextNode(data)
            father.appendChild(tag)

     build(root, structure[rootName])
     return doc.toxml(encoding="utf-8")



