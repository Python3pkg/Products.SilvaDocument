"""
module for providing base xml element/attribute classes.

a namespace (silva and html currently) uses the default
behaviour of the elements contained here.

Note: 
   There is no xml-namespace support up to now.

   The actual transformations are in separate 
   module and don't depend on Zope or Silva. They do
   depend on a DOM-parser (and thus share the
   dependcy on PyXML).

the scheme used for the transformation roughly
follows the ideas used with XIST.  Note that we
can't use XIST itself (which is the upgrade idea)
as long as silva is running on a Zope version that 
doesn't allow python2.2 or better.

"""

__author__='Holger P. Krekel <hpk@trillke.net>'
__version__='$Revision: 1.4 $'

# we only have these dependencies so it runs with python-2.2

import re 
from UserList import UserList as List
from UserDict import UserDict as Dict
from Products.Silva.i18n import translate as _

class Context:
    def __init__(self, **kw):
        self.__dict__.update(kw)
        self.resultstack = []
        self.tablestack = []

class _dummy:
    """ for marking no-values """
    pass

def build_pathmap(node):
    """ return a list of path-node tuples.

    a path is a list of path elements (tag names)
    """
    l = isinstance(node, Element) and [([], node)] or []
    tags = hasattr(node, 'find') and node.find()
    if not tags:
        return l
    for tag in tags:
        for path, subtag in build_pathmap(tag):
            path.insert(0, tag.name())
            l.append((path, subtag))
    return l

class Node:
    def _matches(self, tag):
        if type(tag) == type(()):
            for i in tag:
                if self._matches(i):
                    return 1
        elif type(tag) in (type(''),type(u'')):
            return self.name()==tag
        elif tag is None:
            return 1
        else:
            return issubclass(self.__class__, tag)

    def __eq__(self, other):
        raise _("not implemented, override in inheriting class")

    def name(self):
        """ return name of tag """
        return getattr(self, 'xmlname', self.__class__.__name__)

    def hasattr(self, name):
        """ return true if the attribute 'name' is an attribute name of this tag """
        return self.attr.__dict__.has_key(name)

    def getattr(self, name, default=_dummy):
        """ return xml attribute value or a given default. 

        if no default value is set and there is no attribute
        raise an AttributeError. 
        """
        if default is not _dummy:
            ret = getattr(self.attr, name, default)
            if ret is None:
                return default
            return ret

        if vars(self.attr).has_key(name):
            return getattr(self.attr, name)
        message = _("${name} attribute not found on tag ${self}")
        message.set_mapping({'name': name, 'self': self})
        raise AttributeError,  message

    def conv(self):
        return self.convert(Context())

    def query_one(self, path):
        """ return exactly one tag pointed to by a simple 'path' or raise a ValueError"""
        dic = self.query(path)
        if len(dic) == 0:
            message = _("no ${path} element")
            message.set_mapping({'path': path})
            raise ValueError,  message
        elif len(dic) == 1 and len(dic.values()[0]) == 1:
            return dic.values()[0][0]
        else:
            message = _("more than one ${path} element")
            message.set_mapping({'path': path})
            raise ValueError, message

    def query(self, querypath):
        """ return a dictionary with path -> node mappings matching the querypath. 

        querypath has the syntax 

            name1/name2/... 

        and each name can be 

            *   for any children tag or 
            **  for any children tag in the complete subtree

        and it can look like "one|or|theother"  which would match
        tags named eitehr 'one', 'or' or 'theother'. 

        The implementation uses the regular expression module. 
        """

        # compile regular expression match-string
        l = []
        for i in querypath.split('/'):
            if i == '*':
                l.append(r'[^/]+')
            elif i == '**':
                l.append(r'.+')
            elif '*' in i:
                message = _("intermingling * is not allowed ${i}")
                message.set_mapping({'i': i})
                raise ValueError,  message
            elif '|' in i:
                l.append("(%s)" % i)
            else:
                l.append(i)

        searchstring = "/".join(l) + '$'
        rex = re.compile(searchstring)

        # apply regex to all pathes 
        dic = {}
        for path, tag in build_pathmap(self):
            line = "/".join(path)
            if rex.match(line):
                dic.setdefault(line, []).append(tag)
        return dic

class Frag(Node, List):
    """ Fragment of Nodes (basically list of Nodes)"""
    def __init__(self, *content):
        List.__init__(self)
        self.append(*content)

    def __eq__(self, other):
        try:
            return self.asBytes() == other.asBytes()
        except AttributeError:
            return 0

    def __ne__(self, other):
        return not self==other

    def append(self, *others):
        for other in others:
            if not other:
                continue
            if isinstance(other, Frag) or \
               type(other) == type(()) or \
               type(other) == type([]):
                List.extend(self, other)
            else:
                List.append(self, other)

    def convert(self, context):
        try: context = Context(**context)
        except TypeError: pass

        l = Frag()
        context.resultstack.append(l)
        post = self[:]
        while post:
            node = post.pop(0)
            l.append(node.convert(context))
        return context.resultstack.pop() 

    def extract_text(self):
        l = []
        for node in self:
            l.append(node.extract_text())
        return u''.join(l)

    def compact(self):
        node = self.__class__()
        for child in self:
            cchild = child.compact()
            node.append(cchild)
        return node

    def find(self, tag=None, ignore=None):
        node = Frag()
        for child in self:
            if ignore and ignore(child):
                continue
            if child._matches(tag):
                node.append(child)
        return node

    def find_and_partition(self, tag, ignore=lambda x: None):
        pre,match,post = Frag(), Element(), Frag()
        allnodes = self[:]

        while allnodes:
            child = allnodes.pop(0)
            if not ignore(child) and child._matches(tag):
                match = child
                post = Frag(allnodes)
                break
            pre.append(child)
        return pre,match,post

    def find_all_partitions(self, tag, ignore=lambda x: None):
        l = []
        i = 0
        for child in self:
            if not ignore(child) and child._matches(tag):
                l.append((self[:i], child, self[i+1:]))
            i+=1

        return l

    def asBytes(self, encoding='UTF-8'):
        l = []
        for child in self:
            l.append(child.asBytes(encoding))
        return "".join(l)

# the next dict defines a mapping of mangled->unmangled attribute names
html_unmangle_map = {
        'class_': 'class',
        }

class Attr:
    """ an instance of Attr provides a namespace for tag-attributes"""
    def __init__(self, **kw):
        self.__dict__.update(kw)

    def __setattr__(self, name, value):
        name = html_unmangle_map.get(name, name)
        self.__dict__[name] = value

    def __getattr__(self, name):
        return None

class Element(Node):

    singletons = ['br'] # elements that must be singleton in HTML

    def __init__(self, *content, **kw):
        self.attr = Attr()
        #self.parent = None
        newcontent = []
        for child in content:
            try:
                # if child is 'dictish' assume it contains attrs-bindings
                for name, value in child.items(): 
                    setattr(self.attr, name, value)
            except AttributeError:
                if type(child) in (type(''),type(u'')):
                    child = Text(child)
                newcontent.append(child)
        self.content = Frag(*newcontent)
        #for obj in self.content:
            #assert not getattr(obj, 'parent', None)
        #    obj.parent = self

        for name, value in kw.items():
            if value is not None:
                setattr(self.attr, name, value)

    def __eq__(self, other):
        return self.asBytes("UTF8") == other.asBytes("UTF8")

    def __ne__(self, other):
        return not self==other

    def __nonzero__(self):
        return self.name()!=Element.__name__

    def compact(self):
        node = self.__class__()
        node.content = self.content.compact()
        node.attr = Attr(**self.attr.__dict__)
        return node

    def extract_text(self):
        return self.content.extract_text()

    def isEmpty(self):
        tmp = self.compact()
        return len(tmp.content.find())==0

    def find(self, *args, **kwargs):
        return self.content.find(*args, **kwargs)

    def find_and_partition(self, *args, **kwargs):
        return self.content.find_and_partition(*args, **kwargs)

    def find_all_partitions(self, *args, **kwargs):
        return self.content.find_all_partitions(*args, **kwargs)

    def convert(self, context):
        return self

    def __repr__(self):
        return repr(self.asBytes())

    def index(self, item):
        self.content = self.find()
        return self.content.index(item)

    def asBytes(self, encoding='UTF-8'):
        """ return canonical xml-representation  """
        attrlist=[]
        for name, value in vars(self.attr).items():
            if value is None:
                continue

            name = name.encode(encoding)
            if hasattr(value, 'asBytes'):
                value = value.asBytes(encoding)
            elif type(value)==type(u''):
                value = value.encode(encoding)
            else:
                value = value

            attrlist.append('%s="%s"' % (name, value))

        subnodes = self.content.asBytes(encoding)
        attrlist = " ".join(attrlist)

        name = self.name().encode(encoding)
        
        if attrlist:
            start = '<%(name)s %(attrlist)s' % locals()
        else:
            start = '<' + name.encode(encoding)
        if subnodes or name not in self.singletons: 
                return '%(start)s>%(subnodes)s</%(name)s>' % locals()
        else:
            return '%(start)s/>' % locals()

#_________________________________________________________________
#
# special character handling / CharacterData / Text definitions
#_________________________________________________________________

class CharRef:
    pass

class quot(CharRef): "quotation mark = APL quote, U+0022 ISOnum"; codepoint = 34
class amp(CharRef): "ampersand, U+0026 ISOnum"; codepoint = 38
class lt(CharRef): "less-than sign, U+003C ISOnum"; codepoint = 60
class gt(CharRef): "greater-than sign, U+003E ISOnum"; codepoint = 62
#class apos(CharRef): "apostrophe mark, U+0027 ISOnum"; codepoint = 39

class _escape_chars:
    def __init__(self):
        self.escape_chars = {}
        for _name, _obj in globals().items():
            try:
                if issubclass(_obj, CharRef) and _obj is not CharRef:
                    self.escape_chars[unichr(_obj.codepoint)] = u"&%s;" % _name
            except TypeError:
                continue
        self.charef_rex = re.compile(u"|".join(self.escape_chars.keys()))
            
    def _replacer(self, match):
        return self.escape_chars[match.group(0)]

    def __call__(self, ustring):
        return self.charef_rex.sub(self._replacer, ustring)

escape_chars = _escape_chars()

# END special character handling

class CharacterData(Node):
    def __init__(self, content=u""):
        if type(content)==type(''):
            content = unicode(content)
        self.content = content

    def extract_text(self):
        return self.content

    def convert(self, context):
        return self

    def __eq__(self, other):
        try:
            s = self.asBytes('utf8')
            return s == other or s == other.asBytes('utf8')
        except AttributeError:
            pass
    
    def __ne__(self, other):
        return not self==other

    def __hash__(self):
        return hash(self.content)

    def __len__(self):
        return len(self.content)

    def asBytes(self, encoding):
        content = escape_chars(self.content)
        return content.encode(encoding)

    def __str__(self):
        return self.content


class Text(CharacterData):
    def compact(self):
        if self.content.isspace():
            return Text(' ')
        else:
            return self

