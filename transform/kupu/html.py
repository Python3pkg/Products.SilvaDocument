"""
module for conversion from current 

   kupu - (cvs version)
   
       to

   silva (0.9.1) 

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
__version__='$Revision: 1.14 $'

try:
    from transform.base import Element, Text, Frag
except ImportError:
    from Products.SilvaDocument.transform.base import Element, Text, Frag

try:
    import silva
except ImportError:
    from transform.kupu import silva

try:
    from Products.Silva.mangle import Path
except:
    class Path:
        def __call__(self, path1, path2):
            return path2

    Path = Path()

import re

DEBUG=0

TOPLEVEL = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'p', 'pre', 'table', 'img', 'ul', 'ol', 'dl', 'div']
CONTAINERS = ['body', 'td', 'li'] # XXX should only contain li's that are descendant of nlist

def fix_image_links(el, context):
    """finds all links and sees if they contain an image
    
        if an image inside a link is found the link attr of the image will be 
        set to the href of the link
    """
    if not hasattr(context, 'href'):
        context.href = None
    oldhref = context.href
    if el.name() == 'a':
        href = None
        if hasattr(el.attr, 'href'):
            context.href = el.attr.href
    elif el.name() == 'img':
        img.link = context.href
    elif el.name() == 'Text':
        return
    for child in el.find():
        fix_image_links(child, context)
    context.href = oldhref

def fix_tables_and_divs(el, context, tables=None):
    """get all tables and move them to the current position"""
    # XXX I'd rather use el.query for this but that doesn't retain order
    # so I guess I'm going to have to browse the full tree myself
    if el.name() == 'Text':
        return []
    if tables is None:
        foundtables = []
    else:
        foundtables = tables
    for child in el.find():
        if child.name() in ['table', 'div']:
            foundtables.append(child.convert(context))
            child.should_be_removed = 1
        fix_tables_and_divs(child, context, foundtables)
    return foundtables

def fix_toplevel(el, context):
    """place p's around elements that require that"""
    if el.name() == 'Text':
        return silva.p(el.convert(context))
    elif el.name() in CONTAINERS:
        # actually this shouldn't happen, so perhaps we should return 
        # an empty list here...
        return el.convert(context)
    elif el.name() in TOPLEVEL:
        return el.convert(context)
    else:
        return silva.p(el.convert(context))

def find_and_convert_toplevel(el, context, els=None):
    if (el.name() == 'Text' or el.name() in CONTAINERS or 
            (hasattr(el, 'do_not_fix_content') and el.do_not_fix_content())):
        return []
    if  els is None:
        foundels = []
    else:
        foundels = els
    children = el.find()
    for child in children:
        if el.name() in ['ol', 'ul'] and child.name() in ['ol', 'ul']:
            continue
        find_and_convert_toplevel(child, context, foundels)
        if child.name() in TOPLEVEL and child.name() != 'table' and child.name() != 'div':
            foundels.append(child.convert(context))
            child.should_be_removed = 1
        elif child.name() in CONTAINERS:
            continue
    return foundels

reg_ignorable = re.compile('^([ \t\n]|<br[^>]*>)*$')
def get_textbuf(textbuf, context, ptype):
    """given a list of elements this either returns a p element
        if the list contains non-ignorable elements or it will
        return an empty fragment if it doesn't
    """
    frag = Frag(textbuf)
    converted = frag.convert(context).asBytes('UTF-8').strip()
    if not reg_ignorable.search(converted):
        return silva.p(textbuf, type=ptype)
    return Frag()

def fix_structure(inputels, context, allowtables=0):
    """walk through all inputels recursively

        if the current element is a container, place p's around all non-toplevel
        elements, if it's not, move all toplevel elements to the nearest container
    """
    fixedrest = []
    textbuf = []
    ptype = 'normal'
    for el in inputels:
        # flatten p's by ignoring the element itself and walking through it as 
        # if it's contents are part of the current element's contents
        if el.name() == 'p' and allowtables:
            ptype = el.getattr('class', 'normal')
            for child in el.find():
                foundtables = fix_tables_and_divs(child, context)
                foundtoplevel = find_and_convert_toplevel(el, context)
                if (child.name() not in CONTAINERS and 
                        child.name() not in TOPLEVEL):
                    textbuf.append(child.convert(context))
                else:
                    if textbuf:
                        fixedrest.append(get_textbuf(textbuf, context, ptype))
                        textbuf = []
                    fixedrest.append(fix_toplevel(child, context))
                fixedrest += foundtables
                fixedrest += foundtoplevel
            if textbuf:
                fixedrest.append(get_textbuf(textbuf, context, ptype))
                textbuf = []
        else:
            if el.name() == 'p':
                ptype = el.getattr('class', 'normal')
            foundtables = []
            if allowtables:
                foundtables = fix_tables_and_divs(el, context)
            foundtoplevel = find_and_convert_toplevel(el, context)
            if el.name() not in CONTAINERS and el.name() not in TOPLEVEL:
                textbuf.append(el.convert(context))
            else:
                if textbuf:
                    fixedrest.append(get_textbuf(textbuf, context, ptype))
                    textbuf = []
                fixedrest.append(fix_toplevel(el, context))
            fixedrest += foundtables
            fixedrest += foundtoplevel
    if textbuf:
        fixedrest.append(get_textbuf(textbuf, context, ptype))
        textbuf = []
    return fixedrest

def extract_texts(item, context, allow_indexes=0):
    """extract all text content from a tag"""
    res = []
    for i in item.find():
        if i.name() == 'br':
            res.append(Text(u'\n'))
        elif allow_indexes and i.name() == 'a' and not i.getattr('href', None):
            res.append(i.convert(context))
        elif i.name() != 'Text':
            res += extract_texts(i, context, allow_indexes)
        else:
            res.append(i.convert(context))
    return res

def fix_allowed_items_in_heading(items, context):
    """remove all but allowed markup from headers"""
    fixedrest = []
    for item in items:
        if item.name() in ['b', 'strong', 'br'] + TOPLEVEL + CONTAINERS:
            fixedrest += extract_texts(item, context)
        elif item.name() == 'a' and not getattr(item.attr, 'href', None) is None:
            fixedrest += extract_texts(item, context)
        else:
            fixedrest.append(item.convert(context))
    return fixedrest

class html(Element):
    def convert(self, context):
        """ forward to the body element ... """
        context.title = ''
        bodytag = self.find('body')[0]
        return bodytag.convert(context)

class head(Element):
    def convert(self, context):
        """ ignore """
        return Frag()

class script(Element):
    def convert(self, context):
        """ignore"""
        return Frag()

class body(Element):
    """html-body element"""
    def convert(self, context):
        """ contruct a silva_document with id and title
            either from information found in the html-nodes 
            or from the context (where silva should have
            filled in title and id as key/value pairs)
        """
        h2_tag = self.find(tag=h2)
        if not h2_tag:
            rest = self.find()
            title = context.title
        else:
            h2_tag=h2_tag[0]
            title = h2_tag.extract_text()
            rest = self.find(ignore=h2_tag.__eq__) 
        
        # fix images contained in links: the fix_structure call
        # may shuffle them well and place them outside of links, losing
        # the href
        fix_image_links(self, context)

        # add <p> nodes around elements that aren't allowed top-level
        fixedrest = fix_structure(rest, context, 1)
        
        return silva.silva_document(
                silva.title(title),
                silva.doc(
                    fixedrest
                ),
            )

class h1(Element):
    def convert(self, context):
        if hasattr(self, 'should_be_removed') and self.should_be_removed:
            return Frag()
        fixedcontent = fix_allowed_items_in_heading(self.find(), context)
        result = silva.heading(
            fixedcontent,
            type='normal'
        )
        return result

class h2(Element):
    def convert(self, context):
        if hasattr(self, 'should_be_removed') and self.should_be_removed:
            return Frag()
        fixedcontent = fix_allowed_items_in_heading(self.find(), context)
        result = silva.heading(
            fixedcontent,
            type="normal"
            )
        return result

class h3(Element):
    ""
    def convert(self, context):
        if hasattr(self, 'should_be_removed') and self.should_be_removed:
            return Frag()
        fixedcontent = fix_allowed_items_in_heading(self.find(), context)
        result = silva.heading(
            fixedcontent,
            type="normal"
            )
        return self.process_result(result, context)

    # XXX wtf is this?
    def process_result(self, result, context):
        if hasattr(context, 'toplist_result'):
            context.toplist_result.append(result)
        else:
            return result

class h4(h3):
    ""
    def convert(self, context):
        if hasattr(self, 'should_be_removed') and self.should_be_removed:
            return Frag()
        fixedcontent = fix_allowed_items_in_heading(self.find(), context)
        result = silva.heading(
            fixedcontent,
            type="sub"
            )
        return self.process_result(result, context)

class h5(h3):
    """ List heading """
    def convert(self, context):
        """ return a normal heading. note that the h5-to-title
            conversion is done by the html list-tags themselves. 
            Thus h5.convert is only called if there is no
            list context and therefore converted to a subheading.
        """
        if hasattr(self, 'should_be_removed') and self.should_be_removed:
            return Frag()
        fixedcontent = fix_allowed_items_in_heading(self.find(), context)
        result = silva.heading(
            fixedcontent,
            type="subsub",
            )
        return self.process_result(result, context)

class h6(h3):
    def convert(self, context):
        """ this only gets called if the user erroronaously
            used h6 somewhere 
        """
        if hasattr(self, 'should_be_removed') and self.should_be_removed:
            return Frag()
        fixedcontent = fix_allowed_items_in_heading(self.find(), context)
        result = silva.heading(
            fixedcontent,
            type="paragraph",
            )
        return self.process_result(result, context)
    
class h7(h3):
    def convert(self, context):
        """ this only gets called if the user erroronaously
            used h6 somewhere 
        """
        if hasattr(self, 'should_be_removed') and self.should_be_removed:
            return Frag()
        fixedcontent = fix_allowed_items_in_heading(self.find(), context)
        result = silva.heading(
            fixedcontent,
            type="subparagraph",
            )
        return self.process_result(result, context)

class p(Element):
    """ the html p element can contain nodes which are "standalone"
        in silva-xml. 
    """
    def convert(self, context):
        if hasattr(self, 'should_be_removed') and self.should_be_removed:
            return Frag()
        for child in self.find():
            if child.name() != 'br':
                return silva.p(self.content.convert(context),
                                    type=self.getattr('class', 'normal'))
        return Frag(
        )

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
        hadctx = hasattr(context, 'toplist_result')
        if not hadctx:
            context.toplist_result = context.resultstack[-1]
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

        if not hadctx:
            del context.toplist_result 
        return result

    def is_nlist(self, context):
        for i in self.content.compact():
            if i.name()!='li':
                return 1
        if (self.query('**/img') or self.query('**/p') or 
                self.query('**/table') or self.query('**/ul') or
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
            else:
                lis.append(silva.li(el.convert(context)))

        return silva.list(
            lis,
            type=type
        )

    def convert_nlist(self, context):

        type = self.get_type()
        
        # only allow list items in here
        lis = []
        for el in self.find():
            if el.name() == 'li':
                lis.append(el.convert(context, 1))
            else:
                if lis:
                    lis[-1] = silva.li(lis[-1].content, el.convert(context))
                else:
                    lis.append(silva.li(el.convert(context)))

        return silva.nlist(
            lis,
            type=type)

    def get_type(self):
        curtype = getattr(self.attr, 'type', None)
        if curtype is None:
            curtype = getattr(self.attr, 'type')

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
            
        if context.listtype == 'nlist':
            content = []
            for child in self.find():
                content.append(fix_toplevel(child, context))
            return silva.li(
                        Frag(content)
                    )
        else:
            return silva.li(
                self.content.convert(context)
            )

class strong(Element):
    def convert(self, context):
        return silva.strong(
            self.content.convert(context),
            )

class b(strong):
    pass

class em(Element):
    def convert(self, context):
        return silva.em(
            self.content.convert(context),
            )

class i(em):
    pass

class u(Element):
    def convert(self, context):
        return silva.underline(
            self.content.convert(context),
            )

class sup(Element):
    def convert(self, context):
        return silva.super(
            self.content.convert(context),
            )

class sub(Element):
    def convert(self, context):
        return silva.sub(
            self.content.convert(context),
            )
            
class a(Element):
    def convert(self, context):
        # XXX needs to become empty, but there's a bug in the attr code
        title = getattr(self.attr, 'title', '')
        if title is None:
            title = ''
        if (hasattr(self.attr, 'name') and (not hasattr(self.attr, 'href') or
                self.attr.href == '#' or self.attr.href is None)):
            text = ''.join([t.convert(context).asBytes('UTF-8') for t in extract_texts(self, context)])
            textnode = Frag()
            if text and (text[0] != '[' or text[-1] != ']'):
                textnode = Text(text)
            return Frag(textnode,
                        silva.index(
                                name=self.attr.name,
                                title=title,
                                )
                            )
        elif hasattr(self.attr, 'href') and self.attr.href is not None:
            url = self.getattr('href', 'http://www.infrae.com')
            target = getattr(self.attr, 'target', '')
            #if target is None:
            #    target = ''

            try:
                img = self.query_one('img')
            except ValueError:
                content = self.content.convert(context)
                return silva.link(
                    content,
                    url=url,
                    target=target,
                    title=title,
                    )
            else:
                image = img.convert(context)
                if not image:
                    return Frag()
                alignment = img.getattr('alignment')
                if alignment == 'default' or alignment is None:
                    alignment = ''
                image.attr.alignment = alignment
                if not hasattr(image, 'attr'):
                    # empty frag
                    return image
                if url == '%s?hires' % img.attr.src:
                    image.attr.link_to_hires = '1'
                else:
                    image.attr.link_to_hires = '0'
                    image.attr.link = url
                image.attr.target = target
                image.attr.title = title
                return image
        else:
            return Frag()

class img(Element):
    def convert(self, context):
        if hasattr(self, 'should_be_removed') and self.should_be_removed:
            return Frag()
        from urlparse import urlparse
        src = 'unknown'
        if (hasattr(self.attr, 'src')
                and hasattr(self.attr.src, 'content')):
            src = self.attr.src.content
        src = urlparse(src)[2]
        if src.endswith('/image'):
            src = src[:-len('/image')]
        # turn path into relative if possible
        modelpath = context.model.aq_parent.getPhysicalPath()
        src = '/'.join(Path(modelpath, src.split('/')))
        alignment = self.attr.alignment
        if alignment == 'default' or alignment is None:
            alignment = ''
        if self.hasattr('link_to_hires') and self.getattr('link_to_hires') == '1':
            return silva.image(
                        self.content.convert(context),
                        path = src,
                        link = '%s?hires' % src,
                        alignment = alignment,
                        target = self.getattr('target', '_self'),
                        link_to_hires = '1',
                        title = self.getattr('title', ''),
                    )
        else:
            return silva.image(
                        self.content.convert(context),
                        path = src,
                        link = self.getattr('link', ''),
                        alignment = alignment,
                        target = self.getattr('target', '_self'),
                        link_to_hires = '0',
                        title = self.getattr('title', ''),
                    )

class br(Element):
    def convert(self, context):
        return silva.br()

class pre(Element):
    def compact(self):
        return self

    def convert(self, context):
        if hasattr(self, 'should_be_removed') and self.should_be_removed:
            return Frag()
        return silva.pre(
            extract_texts(self.content, context)
        )

class table(Element):
    alignmapping = {'left': 'L',
                    'right': 'R',
                    'center': 'C'}
    def convert(self, context):
        if hasattr(self, 'should_be_removed') and self.should_be_removed:
            return Frag()
        rows = self.content.find('tr')
        highest = 0
        if len(rows)>0:
            for r in rows:
                cols = len(r.find('td'))
                if cols > highest:
                    highest = cols
        # create the column info
        colinfo = []
        for row in rows:
            cells = row.find('td')
            if len(cells):
                for cell in cells:
                    align = 'left'
                    if hasattr(cell, 'attr'):
                        align = self.alignmapping.get(getattr(cell.attr, 'align')) or 'L'
                        # nasty, this assumes the last char of the field is a %-sign
                    width = '1'
                    if hasattr(cell, 'attr'):
                        width = getattr(cell.attr, 'width', None)
                        if width is not None:
                            width = str(width)[:-1].strip() or '1'
                        else:
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
        tableheadings = self.content.find('th')
        # is it non-header row? 
        if not tableheadings:
            cells = [e.convert(context, 1) for e in self.find('td')]
            return silva.row(
                cells
            )

        texts = extract_texts(self, context, 1)

        return silva.row_heading(
            texts
        )

class td(Element):
    def convert(self, context, parentisrow=0):
        if not parentisrow:
            return Frag()
        rest = self.find()
        fixedrest = fix_structure(rest, context)
        return silva.field(
            fixedrest
        )

class th(Element):
    def convert(self, context, parentisrow=0):
        raise ValueError, "<th> elements should be extracted by the containing row"

class div(Element):
    def convert(self, context):
        if hasattr(self, 'should_be_removed') and self.should_be_removed:
            return Frag()
        if self.attr.toc_depth:
            return silva.toc(
                toc_depth=self.attr.toc_depth
            )
        elif self.getattr('is_citation', None):
            content = fix_structure(self.content, context)
            return silva.cite(
                [silva.author(self.attr.author), 
                silva.source(self.attr.source),
                Frag(content)]
            )
        elif self.attr.source_id:
            content = []
            for key, value in self.attr.__dict__.items():
                if key != 'source_id' and key != 'class':
                    content.append(silva.parameter(unicode(str(value), 'UTF-8'), key=key))
            return silva.source(
                        Frag(content), 
                        id=self.attr.source_id,
                        class_=self.attr.class_
                    )
        else:
            return Frag(fix_structure(self.content, context))

    def do_not_fix_content(self):
        return 1

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
                title=self.attr.title
            )

class acronym(Element):
    def convert(self, context):
        return silva.acronym(
                self.content.convert(context),
                title=self.attr.title
            )

"""
current mapping of tags with silva
h1  :  not in use, reserved for (future) Silva publication
       sections and custom templates
h2  :  title
h3  :  heading
h4  :  subhead
h5  :  list title
"""

def debug_hook():
    from transform.Transformer import EditorTransformer
    from transform.base import Context
    data = '<html><head><title>Foo</title></head><body><p><ol><li>foo<ol><li>bar</li></ol></li></ol></p></body></html>'
    data = '<html><head><title>Whatever</title></head><body><h2>foo</h2><ol type="1"><li>dfsfd</li><li>sdfdfs</li><ol><li>dsklfsdfjsfldk</li></ol><li>fsdsdf</li></ol></body></html>'
    ctx = Context(url='http://debris.demon.nl/foo.html')
    transformer = EditorTransformer(editor='kupu')
    node = transformer.to_source(targetobj=data, context=ctx)[0]
    output = node.asBytes(encoding='UTF-8')
    print output

if __name__ == '__main__':
    debug_hook()
