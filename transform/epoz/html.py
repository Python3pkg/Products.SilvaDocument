"""
module for conversion from current 

   epoz - (cvs version)
   
       to

   silva (0.9.1) 

This transformation tries to stay close to
how silva maps its xml to html. 

There are tests for this transformation in 

    Silva/tests/test_epoztransformation.py

please make sure to run them if you change anything here.

the notation used for the transformation roughly
follows the ideas used with XIST (but has a simpler implementation).
Note that we can't use XIST itself as long as 
silva is running on a Zope version that 
doesn't allow python2.2

"""

__author__='holger krekel <hpk@trillke.net>'
__version__='$Revision: 1.1.2.1 $'

try:
    from transform.base import Element, Text, Frag
except ImportError:
    from Products.SilvaDocument.transform.base import Element, Text, Frag

import silva

DEBUG=0

def fix_toplevel(inputels, context):
    # add <p> nodes around elements that aren't allowed top-level
    fixedrest = []
    textbuf = []
    for el in inputels:
        if el.name() in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'table', 'p', 'pre', 'img', 'ul', 'ol', 'dl']:
            if textbuf:
                fixedrest.append(silva.p(textbuf))
                textbuf = []
            fixedrest.append(el.convert(context))
        else:
            textbuf.append(el.convert(context))
    if textbuf:
        fixedrest.append(silva.p(textbuf))
        textbuf = []
    return fixedrest


class html(Element):
    def convert(self, context):
        """ forward to the body element ... """
        bodytag = self.find('body')[0]
        return bodytag.convert(context)

class head(Element):
    def convert(self, context):
        """ ignore """
        return u''

class script(Element):
    def convert(self, context):
        """ignore"""
        return u''

class body(Element):
    "html-body element"
    def convert(self, context):
        """ contruct a silva_document with id and title
            either from information found in the html-nodes 
            or from the context (where silva should have
            filled in title and id as key/value pairs)
        """
        h2_tag = self.find(tag=h2)
        if not h2_tag:
            rest = self.find()
            title, id = context.title, context.id
        else:
            h2_tag=h2_tag[0]
            title = h2_tag.extract_text()
            rest = self.find(ignore=h2_tag.__eq__) 
            try:
                id = h2_tag.attr.silva_id
            except AttributeError:
                id = context.id

        # add <p> nodes around elements that aren't allowed top-level
        fixedrest = fix_toplevel(rest, context)

        return silva.silva_document(
                silva.title(title),
                silva.doc(
                    fixedrest
                ),
                id = id
            )

class h1(Element):
    def convert(self, context):
        return silva.heading(
            self.content.extract_text(),
            type='normal'
        )

class h2(Element):
    def convert(self, context):
        return silva.heading(
            self.content.extract_text(),
            type="normal"
            )

class h3(Element):
    ""
    def convert(self, context):
        result = silva.heading(
            self.content.extract_text(),
            type="normal"
            )
        return self.process_result(result, context)

    def process_result(self, result, context):
        if hasattr(context, 'toplist_result'):
            context.toplist_result.append(result)
        else:
            return result

class h4(h3):
    ""
    def convert(self, context):
        result = silva.heading(
            self.content.extract_text(),
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
        result = silva.heading(
            self.content.extract_text(),
            type="subsub",
            )
        return self.process_result(result, context)

class h6(h3):
    def convert(self, context):
        """ this only gets called if the user erroronaously
            used h6 somewhere 
        """
        result = silva.heading(
            self.content.extract_text(),
            type="paragraph",
            )
        return self.process_result(result, context)
    
class h7(h3):
    def convert(self, context):
        """ this only gets called if the user erroronaously
            used h6 somewhere 
        """
        result = silva.heading(
            self.content.extract_text(),
            type="subparagraph",
            )
        return self.process_result(result, context)

class p(Element):
    """ the html p element can contain nodes which are "standalone"
        in silva-xml. 
    """
    toplevel = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'table', 'p', 'pre', 'img', 'ul', 'ol', 'dl']
    def convert(self, context):
        items = []
        type = getattr(self.attr, 'silva_type', None)
        for el in self.find():
            if el.name() in self.toplevel:
                items.append(el.convert(context))
            else:
                items.append(silva.p(el.convert(context)))

        return Frag(
            *items
        )

class ul(Element):
    """ difficult list conversions.

        note that the html list constructs are heavily
        overloaded with respect to their silva source nodes.
        they may come from nlist,dlist,list, their title 
        may be outside the ul/ol tag, there are lots of different
        types and the silva and html type names are different. 

        this implementation currently is a bit hackish.
    """
    default_types = ('disc','circle','square','none')
    default_type = 'disc'

    def convert(self, context):
        hadctx = hasattr(context, 'toplist_result')
        if not hadctx:
            context.toplist_result = context.resultstack[-1]
        if self.is_dlist(context):
            result = self.convert_dlist(context)
        elif self.is_nlist(context):
            result = self.convert_nlist(context)
        else:
            result = self.convert_list(context)

        if not hadctx:
            del context.toplist_result 
        return result

    def is_nlist(self, context):
        if (self.query('**/img') or self.query('**/p') or 
                self.query('**/table') or self.query('**/ul') or
                self.query('**/ol')):
            return 1
        else:
            return 0
        for i in self.content.compact():
            if i.name()!='li':
                return 1

    def convert_list(self, context):
        type = self.get_type()

        return silva.list(
            self.content.convert(context),
            type=type
        )

    def convert_nlist(self, context):

        type = self.get_type()
        """
        lastli = None
        content = Frag()
        for tag in self.content.convert(context):
            name = tag.name()
            if name == 'li':
                lastli = tag
                # tag.content = silva.mixin_paragraphs(tag.content)
            elif tag.compact():
                #if not lastli:
                tag = silva.li(tag)
                #else:
                #    lastli.content.append(tag)
                #    lastli = None
                #    continue
            content.append(tag)
        """
        content = self.content
        for i in range(len(content)):
            tag = content[i]
            li = silva.li(fix_toplevel(tag.find(), context))
            content[i] = li
        res = silva.nlist(
            content,
            type=type)
        return res

    def get_type(self):
        curtype = getattr(self.attr, 'type', None)
        if curtype is None:
            curtype = getattr(self.attr, 'silva_type')

        if type(self.default_types) != type({}):
            if curtype not in self.default_types:
                curtype = self.default_type
        else:
            curtype = self.default_types.get(curtype, self.default_type)
        return curtype

    def is_dlist(self, context):
        for item in self.find('li'):
            font = item.find('font')
            if len(font)>0 and getattr(font[0].attr, 'color', None)=='green':
                return 1
        
    def convert_dlist(self, context):
        tags = []
        for item in self.find('li'):
            pre,font,post = item.find_and_partition('font')
            if font and getattr(font.attr, 'color', None) == 'green':
                tags.append(silva.dt(font.content.convert(context)))
            else:
                tags.append(silva.dt())

            if post:
                try: 
                    post[0].content = post[0].content.lstrip()
                except AttributeError:
                    pass

            tags.append(silva.dd(post.convert(context)))

        return silva.dlist(
            type='normal',
            *tags
            )

class ol(ul):
    default_types = ('1', 'a', 'A', 'i', 'I')
    default_type = '1'

class XXXol(Element):

    # XXX the following is not used, is it? 
    # and always returning an 'nlist' violates round-trip consistency,
    # i.e. you pass in a non-nested list but always get out a nested one
    # please if you change this don't forget to run 
    # tests/test_epoztransformation.py which tests such roundtrip consistencies

    class_to_type = {'decimal': '1',
                        'upper-roman': 'A',
                        'lower-roman': 'a',
                        'upper-alpha': 'I',
                        'lower-alpha': 'i',
                        }
                        
    def convert(self, context):
        return silva.nlist(
            self.content.convert(context),
            type = self.getattr('type'),
            )

class li(Element):
    def convert(self, context):
        return silva.li(
                self.content.convert(context)
            )

class dlist(Element):
    def convert(self, context):
        return silva.dlist(
            self.content.convert(context)
        )

class dt(Element):
    def convert(self, context):
        return silva.dt(
            self.content.convert(context)
        )

class dd(Element):
    def convert(self, context):
        return silva.dd(
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
        if hasattr(self.attr, 'href'):
            url=self.getattr('href', 'http://www.infrae.com') 

            try:
                img = self.query_one('img')
            except ValueError:
                return silva.link(
                    self.content.convert(context),
                    url=url,
                    )
            else:
                image = img.convert(context)
                image.attr.link = url
                return image
        elif hasattr(self.attr, 'name'):
            return silva.index(
                self.content.convert(context),
                name=self.attr.name
                )

class img(Element):
    def convert(self, context):
        from urlparse import urlparse
        src = 'unknown'
        if (hasattr(self.attr, 'src')
                and hasattr(self.attr.src, 'content')):
            src = self.attr.src.content
        src = urlparse(src)[2]
        if src.endswith('/image'):
            src = src[:-len('/image')]
        return silva.image(
            self.content.convert(context),
            path=src,
            link=self.getattr('link','nolink'),
            alignment = self.attr.alignment,
            )

class br(Element):
    def convert(self, context):
        return silva.br()

class pre(Element):
    def compact(self):
        return self

    def convert(self, context):
        return silva.pre(
            self.content.convert(context)
        )

class table(Element):
    alignmapping = {'left': 'L',
                    'right': 'R',
                    'center': 'C'}
    def convert(self, context):
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
                            width = str(width)[:-1]
                        else:
                            width = '1'
                    colinfo.append('%s:%s' % (align, width))
                colinfo = ' '.join(colinfo)
                break
        return silva.table(
                self.content.convert(context),
                columns=str(highest),
                column_info = colinfo, 
                type = self.getattr('class', 'plain'),
            )

class tr(Element):
    def convert(self, context):
        tableheadings = self.content.find('th')
        # is it non-header row? 
        if not tableheadings:
            return silva.row(
                self.content.convert(context)
            )

        # merge all headings and make one silva-xml row_heading
        l = []
        for th in tableheadings:
            l.append(th.extract_text().encode('utf8'))

        return silva.row_heading(
            unicode(" ".join(l), 'utf8')
        )

class td(Element):
    def convert(self, context):
        rest = self.find()
        rest = fix_toplevel(rest, context)
        return silva.field(
            rest # self.content.convert(context)
        )

class th(Element):
    def convert(self, context):
        raise ValueError, "<th> elements should be extracted by the containing row"


"""
current mapping of tags with silva
h1  :  not in use, reserved for (future) Silva publication
       sections and custom templates
h2  :  title
h3  :  heading
h4  :  subhead
h5  :  list title
"""
