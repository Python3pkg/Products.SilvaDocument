"""
module for conversion from current

   kupu - (cvs version)

       to

   silva (1.2)

This transformation tries to stay close to
how silva maps its xml to html.

There are tests for this transformation in

    Silva/tests/test_kuputransformation.py

please make sure to run them if you change anything here.

the notation used for the transformation roughly
follows the ideas used with XIST (but has a simpler implementation).
Note that we can't use XIST itself as long as
silva is running on a Zope version that
doesn't allow python2.2

"""

__author__='holger krekel <hpk@trillke.net>'
__version__='$Revision: 1.39 $'

import re
from urlparse import urlparse

from zExceptions import NotFound

from Products.SilvaDocument.transform.base import Element, Text, Frag
from silva.core.interfaces import IPath, IImage
from Products.Silva.mangle import Path

import silvaformat
silva = silvaformat

DEBUG=0

TOPLEVEL = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'p', 'pre', 'table', 'img', 'ul', 'ol', 'dl', 'div']
CONTAINERS = ['body', 'td', 'li', 'th'] # XXX should only contain li's that are descendant of nlist


def is_table_or_source(node):
    """tell you if the node is a table or a code source.
    """
    return (node.name() == 'table' or
            (node.name() == 'div' and
             (node.getattr('source_id', None) or
              node.getattr('source_title', None))))


def retrieve_tables_and_sources(node, context, tables=None):
    """find and convert all tables and code sources, and remove them
    this get call by table and list content as wellfrom the document
    follow
    """
    if (node.name() == 'Text' or
        hasattr(node, 'should_be_removed')):
        return []
    if tables is None:
        tables = []

    if is_table_or_source(node):
        tables.append(node.convert(context))
        node.should_be_removed = 1

    for child in node.find():
        retrieve_tables_and_sources(child, context, tables)
    return tables


def is_toplevel_element(node):
    """tell you if the node is something that should be a top level
    element.
    """
    # this is the case you have an image with a link
    if node.name() == 'a':
        children = node.find()
        if len(children) == 1:
            child = children[0]
            if child.name() == 'img':
                # the next line prevent to consider the image as a top
                # level element as well
                child.is_not_top_level = lambda: 1
                return True

    return (node.name() in TOPLEVEL and not is_table_or_source(node))


def retrieve_toplevel_elements(node, context, elements=None):
    """find and convert all toplevel element type, and remove them of
    the document flow (in fact like retrieve_table does).
    """
    if (node.name() == 'Text' or node.name() in CONTAINERS or
        (hasattr(node, 'is_not_top_level') and node.is_not_top_level()) or
        hasattr(node, 'should_be_removed')):
        return []
    if  elements is None:
        elements = []

    if is_toplevel_element(node):
        elements.append(node.convert(context))
        node.should_be_removed = 1

    children = node.find()
    for child in children:
        if hasattr(child, 'should_be_removed'):
            continue
        if node.name() in ['ol', 'ul'] and child.name() in ['ol', 'ul']:
            continue
        retrieve_toplevel_elements(child, context, elements)

    return elements


reg_ignorable = re.compile('^([ \t\n]|<br[^>]*>)*$')
def build_paragraph(nodes, context, ptype):
    """given a list of elements this either returns a p element
    if the list contains non-ignorable elements or it will
    return an empty fragment if it doesn't
    """
    frag = Frag(nodes)
    converted = frag.convert(context).asBytes('UTF-8').strip()
    if not reg_ignorable.search(converted):
        return silva.p(nodes, type=ptype)
    return Frag()


def fix_structure(nodes, context, allow_tables=0):
    """this goes through the document and convert it, move some
    components (table, top level elements) around in order to clean it.

    this get call by table and list content as well.
    """
    result = []                 # Contain the converted document
    paragraph_buffer = []       # Contain nodes to create a new paragraph

    def get_paragraph_type(node):
        ptype = str(node.getattr('class', 'normal'))
        if ptype not in ['normal', 'lead', 'annotation']:
            ptype = 'normal'
        return ptype

    def flush_paragraph(ptype='normal'):
        # This finish the current paragraph, and add it to the result
        if paragraph_buffer:
            result.append(build_paragraph(paragraph_buffer, context, ptype))
            del paragraph_buffer[:]

    def convert_node(node, paragraph_type):
        # This convert the given node to silva format. Tables and top
        # level elements are extracted from the node and added
        # afterward.
        tables = []
        if allow_tables:
            tables = retrieve_tables_and_sources(node, context)
        toplevel = retrieve_toplevel_elements(node, context)
        if not hasattr(node, 'should_be_removed'):
            # Node have not been marked to be removed, so it is no table
            # or top level element.
            paragraph_buffer.append(node.convert(context))
        else:
            # It is a table or a top level element
            flush_paragraph(paragraph_type)
        result.extend(tables)
        result.extend(toplevel)

    ptype = 'normal'
    for node in nodes:
        # flatten p's by ignoring the element itself and walking through it as
        # if it's contents are part of the current element's contents
        if node.name() == 'p':
            ptype = get_paragraph_type(node)
            for child in node.find():
                convert_node(child, ptype)
            flush_paragraph(ptype)
        else:
            convert_node(node, ptype)
    flush_paragraph(ptype)
    return result


def extract_texts(node, context, allow_indexes=0):
    """extract all text content from a tag
    """
    result = []
    for child in node.find():
        if child.name() == 'br':
            result.append(Text(u'\n'))
        elif (allow_indexes and child.name() == 'a' and
              not child.getattr('href', None)):
            result.append(child.convert(context))
        elif child.name() != 'Text':
            result += extract_texts(child, context, allow_indexes)
        else:
            result.append(child.convert(context))
    return result


def fix_allowed_items_in_heading(items, context):
    """remove all but allowed markup from headers"""
    result = []
    for item in items:
        if item.name() in ['b', 'strong', 'br'] + TOPLEVEL + CONTAINERS:
            result += extract_texts(item, context)
        else:
            result.append(item.convert(context))
    return result


# Element to ignore
class head(Element):

    def convert(self, context):
        return Frag()


class script(Element):

    def convert(self, context):
        return Frag()


class style(Element):

    def convert(self, context):
        return Frag()


# Document elements
class html(Element):

    def convert(self, context):
        """ forward to the body element ... """
        context.title = ''
        body = self.find('body')[0]
        return body.convert(context)


class body(Element):
    """html-body element
    """

    def convert(self, context):
        """ contruct a silva_document with id and title
            either from information found in the html-nodes
            or from the context (where silva should have
            filled in title and id as key/value pairs)
        """
        title_tag = self.find(tag=h1)
        if not title_tag:
            title_tag = self.find(tag=h2)
        if not title_tag:
            title = context.title
            document = self.find()
        else:
            title_tag = title_tag[0]
            title = title_tag.extract_text()
            document = self.find(ignore=title_tag.__eq__)

        # add <p> nodes around elements that aren't allowed top-level
        document = fix_structure(document, context, allow_tables=1)

        return silva.silva_document(
            silva.title(title),
            silva.doc(document))


class h1(Element):
    """Headers h1 are rendered as normal Silva headers.
    """
    header_type = 'normal'

    def convert(self, context):
        if hasattr(self, 'should_be_removed') and self.should_be_removed:
            return Frag()
        fixedcontent = fix_allowed_items_in_heading(self.find(), context)
        return silva.heading(fixedcontent, type=self.header_type)


class h2(h1):
    """Headers h2 are rendered as normal Silva headers.
    """
    pass


class h3(h1):
    """Headers h3 are rendered as normal Silva headers.
    """
    pass


class h4(h1):
    """Header h4 are rendered as sub Silva headers.
    """
    header_type = 'sub'


class h5(h3):
    """Header h4 are rendered as subsub Silva headers.
    """
    header_type = 'subsub'


class h6(h1):
    header_type = 'paragraph'

    def convert(self, context):
        """This only gets called if the user erroneously
        used h6 somewhere.
        """
        if hasattr(self, 'should_be_removed') and self.should_be_removed:
            return Frag()
        fixedcontent = fix_allowed_items_in_heading(self.find(), context)
        if (hasattr(self, 'attr') and hasattr(self.attr, 'silva_type')
            and self.attr.silva_type == 'sub'):
            self.header_type = 'subparagraph'
        result = silva.heading(
            fixedcontent, type=self.header_type)
        return result


class h7(h1):
    """Header h7 (is it HTML ?) are rendered as subparagraph Silva headers.
    """
    header_type = 'subparagraph'



class p(Element):
    """ the html p element can contain nodes which are "standalone"
        in silva-xml.
    """
    def convert(self, context):
        if hasattr(self, 'should_be_removed') and self.should_be_removed:
            return Frag()
        # return a p, but only if there's any content besides whitespace
        # and <br>s
        for child in self.find():
            if child.name() != 'br':
                type = self.getattr('silva_type', 'normal')
                if type not in ['normal', 'lead', 'annotation']:
                    type = 'normal'
                return silva.p(self.content.convert(context), type=type)
        return Frag()


class ul(Element):
    """ difficult list conversions.

        note that the html list constructs are heavily
        overloaded with respect to their silva source nodes.
        they may come from nlist,list, their title
        may be outside the ul/ol tag, there are lots of different
        types and the silva and html type names are different.

        this implementation currently is a bit hackish.
    """
    default_types = ('disc','circle','square','none')
    default_type = 'disc'

    def convert(self, context):
        if hasattr(self, 'should_be_removed') and self.should_be_removed:
            return Frag()
        if self.is_nlist(context):
            curlisttype = getattr(context, 'listtype', None)
            context.listtype = 'nlist'
            result = self.convert_nlist(context)
            if curlisttype is not None:
                context.listtype = curlisttype
            else:
                del context.listtype
        else:
            curlisttype = getattr(context, 'listtype', None)
            context.listtype = 'list'
            result = self.convert_list(context)
            if curlisttype is not None:
                context.listtype = curlisttype
            else:
                del context.listtype
        return result

    def is_nlist(self, context):
        for i in self.content.compact():
            if i.name() in ['ol', 'ul']:
                # browsers allow lists as direct children of lists, in Silva
                # this should get appended to the previous list element content
                # to get a similar result
                return 1
        if (self.query('**/img') or self.query('**/p') or
            self.query('**/table') or self.query('**/ul') or
            self.query('**/h3') or self.query('**/h4') or
            self.query('**/h5') or self.query('**/h6') or
            self.query('**/ol') or self.query('**/pre')):
            return 1
        else:
            return 0

    def convert_list(self, context):
        type = self.get_type()

        # only allow list items in here
        lis = []
        for el in self.find():
            if el.name() == 'li':
                lis.append(el.convert(context, 1))

        return silva.list(lis, type=type)

    def convert_nlist(self, context):

        type = self.get_type()

        # only allow list items in here
        lis = []
        for el in self.find():
            if el.name() == 'li':
                lis.append(el.convert(context, 1))
            elif el.name() in ['ol', 'ul']:
                # filter out non-li elements

                # note that we need to treat nested lists a bit specially
                # because of the way they get rendered - if we place them in a
                # seperate li, they will get multiple dots, so they need to be
                # attached to the parent list item instead (of course Kupu
                # won't feed it to us like that - instead we get invalid XHTML)
                if lis:
                    lis[-1] = silva.li(lis[-1].content, el.convert(context))
                else:
                    lis.append(silva.li(el.convert(context)))

        return silva.nlist(lis, type=type)

    def get_type(self):
        curtype = getattr(self.attr, 'type', None)

        if type(self.default_types) != type({}):
            if curtype not in self.default_types:
                curtype = self.default_type
        else:
            curtype = self.default_types.get(curtype, self.default_type)
        return curtype


class ol(ul):
    default_types = ('1', 'a', 'A', 'i', 'I')
    default_type = '1'


class li(Element):
    def convert(self, context, parentislist=0):
        if not parentislist:
            return Frag()

        # remove all top-level divs, IE seems to place them for some
        # unknown reason and they screw stuff up in add_paragraphes
        children = []
        for child in self.find():
            if child.name() == 'div':
                for cchild in child.find():
                    children.append(cchild)
            else:
                children.append(child)

        if context.listtype == 'nlist':
            content = fix_structure(self.find(), context)
            return silva.li(Frag(content))
        else:
            content = []
            for child in children:
                content.append(child.convert(context))
            return silva.li(content)


# Text formatting elements
class strong(Element):

    def convert(self, context):
        return silva.strong(self.content.convert(context))


class b(strong):
    pass


class em(Element):

    def convert(self, context):
        return silva.em(self.content.convert(context))


class i(em):
    pass


class u(Element):

    def convert(self, context):
        return silva.underline(self.content.convert(context))


class sup(Element):

    def convert(self, context):
        return silva.super(self.content.convert(context),)


class sub(Element):

    def convert(self, context):
        return silva.sub(self.content.convert(context))


class br(Element):

    def convert(self, context):
        return silva.br()


# Link and images
class a(Element):

    def convert(self, context):
        title = self.getattr('title', default='')
        name = self.getattr('name', default=None)
        href = self.getattr('href', default='#')
        anchor = self.getattr('silva_anchor', default=None)
        window_target = self.getattr('target', default='')

        link_attributes = {'target': window_target,
                           'title': title,
                           'anchor': anchor}

        if name is not None and href == '#':
            # Case one, we are an anchor
            if self.getattr('class', None) == 'index':
                # index item
                text = ''.join([t.convert(context).asBytes('UTF-8') for
                                t in extract_texts(self, context)])
                textnode = Frag()
                if text and (text[0] != '[' or text[-1] != ']'):
                    textnode = Text(text)
                return Frag(
                    textnode,
                    silva.index(name=name, title=title))
            else:
                # named anchor, probably pasted from some other page
                return Frag(self.content.convert(context))
        elif self.hasattr('silva_reference'):
            # Case of a Silva reference used
            reference_name = str(self.getattr('silva_reference'))
            reference_name, reference = context.get_reference(reference_name)
            assert reference is not None, "Invalid reference"
            target_id = self.getattr('silva_target', '0')
            try:
                target_id = int(str(target_id))
            except ValueError:
                raise AssertionError("Invalid reference target id")
            # The target changed, update it
            if target_id != reference.target_id:
                reference.set_target_id(target_id)
            link_attributes['reference'] = reference_name
            return silva.link(
                self.content.convert(context),
                **link_attributes)
        elif self.hasattr('href'):
            # External links
            url = self.getattr('silva_href', None)
            if url is None:
                url = self.getattr('href', '')
            if unicode(url).startswith('/'):
                # convert to physical path before storing
                url = Text(IPath(context.request).urlToPath(unicode(url)))
            if url:
                link_attributes['url'] = url
            return silva.link(
                self.content.convert(context),
                **link_attributes)
        elif anchor is not None:
            # Link to an anchor on the same page
            return silva.link(
                self.content.convert(context),
                **link_attributes)
        else:
            return Frag()


class img(Element):

   def convert(self, context):
       if hasattr(self, 'should_be_removed') and self.should_be_removed:
           return Frag()

       title = self.getattr('alt', '')
       alignment = self.getattr('alignment', 'default')
       if alignment == 'default':
           alignment = ''

       if self.hasattr('silva_reference'):
           reference_name = str(self.getattr('silva_reference'))
           reference_name, reference = context.get_reference(reference_name)
           assert reference is not None, "Invalid reference"
           target_id = self.getattr('silva_target', '0')
           try:
               target_id = int(str(target_id))
           except ValueError:
               raise AssertionError("Invalid reference target id")
           # The target changed, update it
           if target_id != reference.target_id:
               reference.set_target_id(target_id)

           return silva.image(
               self.content.convert(context),
               reference=reference_name,
               alignment=alignment,
               title=title)

       # This is an old url-based image link
       src = getattr(self.attr, 'src', None)
       if src is None:
           src = 'unknown'
       elif hasattr(src, 'content'):
           src = src.content
       src = urlparse(str(src))[2]
       src = IPath(context.request).urlToPath(str(src))
       if src.endswith('/image'):
           src = src[:-len('/image')]
       # turn path into relative if possible, traverse to the object to
       # fix an IE problem that adds the current location in front of paths
       # in an attempt to make them absolute, which leads to nasty paths
       # such as '/silva/index/edit/index/edit/foo.jpg'
       try:
           obj = context.model.unrestrictedTraverse(src.split('/'))
           # bail out if obj is not a Silva Image, otherwise the old
           # href value would be lost
           if not IImage.providedBy(obj):
               raise NotFound(src)
       except (KeyError, NotFound):
           pass
       else:
           modelpath = context.model.aq_parent.getPhysicalPath()
           src = '/'.join(Path(modelpath, obj.getPhysicalPath()))

       return silva.image(
           self.content.convert(context),
           path=src,
           alignment=alignment,
           title=title)


class pre(Element):

    def compact(self):
        """Don't remove any spaces
        """
        return self

    def convert(self, context):
        if hasattr(self, 'should_be_removed') and self.should_be_removed:
            return Frag()
        return silva.pre(extract_texts(self.content, context))


class table(Element):
    alignmapping = {'left': 'L',
                    'right': 'R',
                    'center': 'C'}
    def convert(self, context):
        if hasattr(self, 'should_be_removed') and self.should_be_removed:
            return Frag()
        self.should_be_removed = 1
        rows = self.content.find('tr')
        highest = 0
        if len(rows)>0:
            for r in rows:
                cols = len(r.find(('td','th')))
                if cols > highest:
                    highest = cols
        # create the column info
        colinfo_attr_value = self.getattr('silva_column_info', None)
        if colinfo_attr_value is not None:
            colinfo = colinfo_attr_value
        else:
            colinfo = []
            for row in rows:
                cells = row.find(('td','th'))
                if len(cells):
                    for cell in cells:
                        align = 'left'
                        if hasattr(cell, 'attr'):
                            align = self.alignmapping.get(
                                        getattr(cell.attr, 'align')) or 'L'
                        # nasty, this assumes the last char of the field is a %-sign
                        width = '1'
                        if hasattr(cell, 'attr'):
                            width = getattr(cell.attr, 'width', None)
                            if width:
                                width = str(width)[:-1].strip() or '1'
                            else:
                                width = '1'
                            if not width or width == '0':
                                width = '1'
                        colinfo.append('%s:%s' % (align, width))
                    colinfo = ' '.join(colinfo)
                    break
        rows = Frag(*[r.convert(context, 1) for r in self.find('tr')])
        return silva.table(
                rows,
                columns=str(highest),
                column_info = colinfo,
                type = self.getattr('class', 'plain'),
            )

class tr(Element):

    def convert(self, context, parentistable=0):
        if not parentistable:
            return Frag()
        return silva.row(
            [cell.convert(context, 1) for cell in self.find(('td','th'))])


class td(Element):

    fieldtype = 'td'

    def convert(self, context, parentisrow=0):
        if not parentisrow:
            return Frag()
        colspan = getattr(self.attr, 'colspan', None)
        attributes = {'fieldtype': self.fieldtype}
        if colspan is not None:
            attributes['colspan'] = colspan
        return silva.field(
            fix_structure(self.find(), context),
            **attributes)

class th(td):

    fieldtype = 'th'


class div(Element):

    def convert(self, context):
        if hasattr(self, 'should_be_removed') and self.should_be_removed:
            return Frag()
        self.should_be_removed = 1
        if self.hasattr('source_id'):
            content = []
            params = {}
            for thing in self.find():
                if thing.name() == 'div':
                    for child in thing.find():
                        if child.name() == 'span':
                            key = child.attr.key.content
                            if child.find():
                                value = child.content[0].content
                            else:
                                value = ''
                            vtype = 'string' # default type
                            if '__type__' in key:
                                vtype = key.split('__type__')[1]
                            if type(value) != unicode:
                                value = unicode(value, 'UTF-8')
                            if vtype == 'list':
                                if not key in params:
                                    params[key] = []
                                params[key].append(value)
                            else:
                                params[key] = value
            for key in params:
                vkey = key
                vtype = 'string'
                if '__type__' in key:
                    vkey, vtype = key.split('__type__')
                if vtype == 'list':
                    value = unicode(
                        str(([x.encode('utf-8') for x in params[key]])),
                        'utf-8')
                else:
                    value = params[key]
                content.append(
                    silva.parameter(
                    value,
                    key=vkey, type=vtype))

            return silva.source(
                        Frag(content),
                        id=self.attr.source_id,
                        class_=self.attr.class_)
        else:
            return Frag(fix_structure(self.content, context))

    def is_not_top_level(self):
        return self.hasattr('source_id')


class span(Element):

    def convert(self, context):
        if hasattr(self, 'should_be_removed') and self.should_be_removed:
            return Frag()
        return Frag(extract_texts(self.content, context))


class dl(Element):

    def convert(self, context):
        if hasattr(self, 'should_be_removed') and self.should_be_removed:
            return Frag()

        children = []
        lastchild = None
        for child in self.find():
            if child.name() == 'dt':
                if lastchild is not None and lastchild.name() == 'dt':
                    children.append(silva.dd(Text(' ')))
                children.append(silva.dt(child.content.convert(context)))
                lastchild = child
            elif child.name() == 'dd':
                if lastchild is not None and lastchild.name() == 'dd':
                    children.append(silva.dt(Text(' ')))
                children.append(silva.dd(child.content.convert(context)))
                lastchild = child
        if lastchild is not None and lastchild.name() == 'dt':
            children.append(silva.dd(Text(' ')))
        return silva.dlist(Frag(children))

class dt(Element):

    def convert(self, context):
        return silva.dt(self.content.convert(context))

class dd(Element):

    def convert(self, context):
        return silva.dd(self.content.convert(context))

class abbr(Element):

    def convert(self, context):
        return silva.abbr(
            self.content.convert(context),
            title=self.attr.title)

class acronym(Element):

    def convert(self, context):
        return silva.acronym(
                self.content.convert(context),
                title=self.attr.title)

