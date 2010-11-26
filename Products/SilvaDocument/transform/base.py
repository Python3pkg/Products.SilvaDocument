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

from UserList import UserList as List
import re
import uuid

from silva.translations import translate as _
from silva.core.references.interfaces import IReferenceService
from zope import component

LINK_REFERENCE_TAG=u"document link"


def determine_browser_from_request(request):
    """Return browser name
    """
    if (request is not None and
        request.get('HTTP_USER_AGENT', '').find('MSIE') > -1):
        return 'IE'
    return 'Mozilla'


class Context(object):
    """Transformation context, passed to all the node during
    transformation. It contains methods to manage references.
    """

    def __init__(self, context, request, reference_name=LINK_REFERENCE_TAG):
        """A Transformation Context is built from a context of
        transformation, which is a version of a versioned content on
        which the transformed XML data is stored, and the request from
        which the transformation is triggered.

        reference_name is used to identify which relations of the
        version are related to the processed XML data.
        """
        self.model = context.get_content()
        self.version = context
        self.request = request
        self.browser = determine_browser_from_request(request)
        self.__reference_name = reference_name
        self.__reference_service = component.getUtility(IReferenceService)
        self.__references_used = set()
        self.__references = {}
        self.resultstack = []
        self.tablestack = []

    def get_reference(self, link_name, read_only=False):
        """Retrieve an existing reference used in the XML.

        If read_only is set to True, when it will fail if the asked
        link is a new one or if it has already been asked.

        Don't call this method twice with the same link name and
        read_only set to False, or it will return a new reference (to
        handle copies).
        """
        if link_name == 'new' or link_name in self.__references_used:
            # This is a new reference, or one that have already been
            # edited. In that case we create a new one, as it might be
            # a copy.
            if read_only:
                raise KeyError(u"Missing reference %s tagged %s" % (
                        self.__reference_name, link_name))
            return self.new_reference()
        reference = self.__references.get(link_name, None)
        if reference is not None:
            self.__references_used.add(link_name)
        return link_name, reference

    def new_reference(self):
        """Create a new reference to be used in the XML.
        """
        reference = self.__reference_service.new_reference(
            self.version, self.__reference_name)
        link_name = unicode(uuid.uuid1())
        reference.add_tag(link_name)
        self.__references[link_name] = reference
        self.__references_used.add(link_name)
        return link_name, reference

    def begin_transform(self):
        """This method should be called by the Transformer before
        starting the transformation process. It should not be called
        by any node.
        """
        self.__references_used = set()
        self.__references = dict(map(
                lambda r: (r.tags[1], r),
                filter(
                    lambda r: r.tags[0] == self.__reference_name,
                    self.__reference_service.get_references_from(
                        self.version))))

    def finish_transform(self):
        """This method should be called by the Transformer after the
        transformation process is done. It should not be called by any
        node.
        """
        for link_name, reference in self.__references.items():
            if link_name not in self.__references_used:
                # Reference has not been used, remove it.
                del self.__reference_service.references[reference.__name__]


_marker = object()


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


class Node(object):

    def _matches(self, tag):
        if isinstance(tag, tuple):
            for i in tag:
                if self._matches(i):
                    return 1
        elif isinstance(tag, basestring):
            return self.name()==tag
        elif tag is None:
            return 1
        else:
            return issubclass(self.__class__, tag)

    def __eq__(self, other):
        raise NotImplementedError

    def name(self):
        """Return name of tag
        """
        return getattr(self, 'xmlname', self.__class__.__name__)

    def hasattr(self, name):
        """Return true if the attribute 'name' is an attribute name
        of this tag
        """
        return self.attr.__dict__.has_key(name)

    def getattr(self, name, default=_marker):
        """Return xml attribute value or a given default.

        if no default value is set and there is no attribute
        raise an AttributeError.
        """
        if default is not _marker:
            ret = getattr(self.attr, name, default)
            if ret is None:
                return default
            return ret

        if vars(self.attr).has_key(name):
            return getattr(self.attr, name)
        message = "%s attribute not found on tag %s" % (name, self)
        raise AttributeError,  message

    def query_one(self, path):
        """Return exactly one tag pointed to by a simple 'path' or
        raise a ValueError.
        """
        dic = self.query(path)
        if len(dic) == 0:
            message = _("no ${path} element", mapping={'path': path})
            raise ValueError,  message
        elif len(dic) == 1 and len(dic.values()[0]) == 1:
            return dic.values()[0][0]
        else:
            message = "more than one %s element" % path
            raise ValueError, message

    def query(self, querypath):
        """Return a dictionary with path -> node mappings matching
        the querypath.

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
                message = _(
                    "intermingling * is not allowed ${i}",
                    mapping={'i': i})
                raise ValueError,  message
            elif '|' in i:
                l.append("(%s)" % i)
            else:
                l.append(i)

        searchstring = "/".join(l) + '$'
        rex = re.compile(searchstring)

        # apply regex to all paths
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

class Attr(object):
    """An instance of Attr provides a namespace for tag-attributes.
    """
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

class amp(CharRef): "ampersand, U+0026 ISOnum"; codepoint = 38
class lt(CharRef): "less-than sign, U+003C ISOnum"; codepoint = 60
class gt(CharRef): "greater-than sign, U+003E ISOnum"; codepoint = 62

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

