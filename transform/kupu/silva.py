"""
module for conversion from current silva (0.9.1) XML to
kupu (HEAD) version HTML. 

the notation used for the transformation roughly
follows the ideas used with XIST (but simpler).  
Note that we can't use XIST itself as long as 
silva is running on a Zope version that 
doesn't allow python2.2.1

"""

__author__='holger krekel <hpk@trillke.net>'
__version__='$Revision: 1.1.2.5 $'

try:
    from transform.base import Element, Frag, Text
except ImportError:
    from Products.SilvaDocument.transform.base import Element, Frag, Text

import html
import operator

_attr_origin=u'silva_origin'
_attr_prefix=u'silva_'

# special attribute used for heuristics when transforming
# back to silva-xml

class SilvaElement(Element):
    def backattr(self):
        """ return dictionary with back attributes
            these attributes are later used for 
            the transformation from html to silvaxml.
        """
        attrs = {}
        for name, value in vars(self.attr).items():
            name = u'silva_'+name
            attrs[name]=value

        attrs[u'silva_origin']=self.name()
        return attrs

    def convert(self, context):
        """ for transformation of silva nodes to 
            html often we just want the content of 
            the node without the surrounding tags. 
        """
        return self.content.convert(context)

# -------------------------------------------------
# SILVA-XML Version 1 conversions to html
# -------------------------------------------------

class silva_document(SilvaElement):
    def convert(self, context):
        node_title = self.find(tag=title)[0]
        node_body = self.find(tag=doc)[0]

        body = html.body(
            html.h2(node_title.convert(context), 
                    silva_origin='silva_document',
                    silva_id=self.attr.id
                    ),
            node_body.convert(context),
            self.backattr()
            )
        return body

    def asBytes(self, *args, **kwargs):
        return SilvaElement.asBytes(self, *args, **kwargs)

class title(SilvaElement): 
    """ us used with documents, list and tables (i guess) """

class doc(SilvaElement):
    """ subtag of silva_document """
    def asBytes(self, *args, **kwargs):
        self.attr.xmlns = 'http://xml.infrae.com/document/0.9.3'
        return SilvaElement.asBytes(self, *args, **kwargs)

class heading(SilvaElement):
    def convert(self, context):
        # some defensive programming here...
        level = self.attr.type
        h_tag = {u'normal' : html.h3, 
                 u'sub': html.h4, 
                 u'subsub': html.h5,
                 u'paragraph': html.h6,
                 u'subparagraph': html.h7,
                 }.get(level, html.h3)

        return h_tag(
            self.content.convert(context),
            )

class p(SilvaElement):
    def convert(self, context):
        return html.p(
            self.content.convert(context),
            silva_type=self.getattr('type', 'normal')
            )

class br(Element):
    def convert(self, context):
        return html.br()

class list(SilvaElement):
    """ Simple lists """
    def convert(self, context):
        listtype = self.getattr('type')
        listtype = listtype or u'none'

        attrs = {}
        if listtype in ['1','i','I','a','A']:
            tag = html.ol
            attrs[u'type']=listtype
        elif listtype in (u'disc',u'square',u'circle'):
            tag = html.ul
        else:
            tag = html.ul

        return tag(
                    self.content.convert(context),
                    attrs,
                    type=listtype,
                )

class nlist(list):
    pass

class li(SilvaElement):
    """ list items """
    def convert(self, context):
        return html.li(
            self.content.convert(context)
            )

class strong(SilvaElement):
    def convert(self, context):
        return html.strong(
            self.content.convert(context)
            )

class underline(SilvaElement):
    def convert(self, context):
        return html.u(
            self.content.convert(context)
            )

class em(SilvaElement):
    def convert(self, context):
        return html.em(
            self.content.convert(context)
            )

class super(SilvaElement):
    def convert(self, context):
        return html.sup(
            self.content.convert(context),
            )

class sub(SilvaElement):
    def convert(self, context):
        return html.sub(
            self.content.convert(context),
            )

class link(SilvaElement):
    def convert(self, context):
        try:
            img = self.query_one('image')
        except ValueError:
            return html.a(
                self.content.convert(context),
                href=self.attr.url,
            )
        else:
            url = str(self.attr.url).strip()
            if url:
                return html.img(
                        img.content.convert(context),
                        src=img.getattr('path'),
                        link=url,
                        target=self.getattr('target', '_self'),
                        alignment=img.getattr('alignment', 'default'),
                )
            else:
                if img.hasattr('link_to_hires') and img.getattr('link_to_hires') == '1':
                    return html.img(
                            img.content.convert(context),
                            src=img.getattr('path'),
                            link_to_hires='1',
                            link='%s/hires_image' % img.getattr('path'),
                            target=img.getattr('target', '_self'),
                            alignment=img.getattr('alignment', 'default'),
                    )
                else:
                    return html.img(
                            img.content.convert(context),
                            src=img.getattr('path'),
                            link_to_hires='0',
                            link=img.getattr('link', ''),
                            target=img.getattr('target', '_self'),
                            alignment=img.getattr('alignment', 'default'),
                    )

class index(SilvaElement):
    def convert(self, context):
        return html.a(
            Text('[%s]' % self.attr.name),
            name=self.attr.name,
            class_='index',
        )

class image(SilvaElement):
    def convert(self, context):
        src = self.attr.path
        try:
            src = src.content
        except AttributeError:
            pass
        if not src:
            src = ''

        if ((not self.hasattr('link') or str(self.getattr('link')).strip() == '')
                and (not self.hasattr('link_to_hires') or self.getattr('link_to_hires') == '0')):
            return html.img(
                        self.content.convert(context),
                        src = src+'/image',
                        target=self.getattr('target', '_self'),
                        alignment=self.getattr('alignment', 'default'),
                  )
        elif not self.hasattr('link') or str(self.getattr('link')).strip() == '':
            return html.img(
                        self.content.convert(context),
                        src='%s/image' % src,
                        link_to_hires='1',
                        target=self.getattr('target', '_self'),
                        alignment=self.getattr('alignment', 'default'),
                    ),
        basesrcpath = src
        link = self.getattr('link')
        if link == '%s/hires_image' % src:
            return html.img(
                        self.content.convert(context),
                        src = '%s/image' % src,
                        link_to_hires='1',
                        target=self.getattr('target', '_self'),
                        alignment=self.getattr('alignment', 'default'),
                    )
        else:
            return html.img(
                        self.content.convert(context),
                        src='%s/image' % src,
                        link_to_hires=self.attr.link_to_hires,
                        link=self.getattr('link', ''),
                        target=self.getattr('target', '_self'),
                        alignment=self.getattr('alignment', 'default'),
                )

class pre(SilvaElement):
    def compact(self):
        return self

    def convert(self, context):
        return html.pre(
            self.content.convert(context),
        )

class table(SilvaElement):
    alignmapping = {'L': 'left',
                    'C': 'center',
                    'R': 'right'}

    def convert(self, context):
        context.tablestack.append(self)
        self.cols = self.compute_colnum()
        self.aligns, self.relwidths = self.compute_aligns_relwidths()
        t = html.table(
            self.content.convert(context),
            self.backattr(),
            cols = self.getattr('columns'),
            cellpadding="0",
            cellspacing="3",
            width="100%",
            #border=self.attrs.get('type') != 'plain' and '1' or None
            #border="1", cellpadding="8", cellspacing="2",
            #class_=self.attrs.get('type')
            )
        t.attr.class_ = self.getattr('type', 'plain')
        context.tablestack.pop()
        return t

    def compute_colnum(self):
        """ return maximum number of colums used in any row """
        colnum = 0
        for row in self.find('row'):
            colnum = max(colnum, len(row.find('field')))
        return colnum

    def compute_aligns_relwidths(self):
        """ return a list with the alignments """
        infos = str(self.attr.column_info).split(' ')
        aligns = [self.alignmapping[i[0]] for i in infos]
        relwidths = [int(i[2:]) for i in infos]
        return aligns, relwidths
   
class row(SilvaElement):
    def convert(self, context):
        relwidths = context.tablestack[-1].relwidths
        units = 100 / reduce(operator.add, relwidths)
        widths = [units * i for i in relwidths]
        aligns = context.tablestack[-1].aligns
        cells = self.find('field')
        if cells:
            for i in range(len(cells)):
                # leave some room for errors
                if len(aligns) > i and len(widths) > i:
                    cells[i].attr.align = aligns[i]
                    cells[i].attr.width = '%s%%' % widths[i]
                else:
                    cells[i].attr.align = aligns[0]
                    cells[i].attr.width = '%s%%' % widths[0]
        return html.tr(
            self.content.convert(context),
        )

class row_heading(SilvaElement):
    def convert(self, context):
        cols = context.tablestack[-1].cols 
        return html.tr(
            html.th(
               self.content.convert(context),
               colspan = str(cols)
            )
        )
  
class field(SilvaElement):
    def convert(self, context):
        return html.td(
            self.content.convert(context),
            #align=self.attr.align,
            #width=self.attr.width
        )

class toc(SilvaElement):
    def convert(self, context):
        depth = str(self.attr.toc_depth) or 1
        multiple_s = 's'
        if int(depth) == 1:
            multiple_s = ''
        depth_string = depth
        if int(depth) == -1:
            depth_string = 'unlimited'
        return html.div(
            Text('Table of Contents (%s level%s)' % (depth_string, multiple_s)),
            toc_depth = depth,
            class_ = 'toc',
            is_toc = '1'
        )

class cite(SilvaElement):
    def convert(self, context):
        author = self.find('author')[0].convert(context)
        source = self.find('source')[0].convert(context)
        content = [p.convert(context) for p in self.find('p')]
        
        return html.div(
            content,
            author=author,
            source=source,
            class_='citation',
            is_citation='1',
        )

class author(SilvaElement):
    def convert(self, context):
        return self.content.convert(context)

class source(SilvaElement):
    def convert(self, context):
        return self.content.convert(context)

def mixin_paragraphs(container):
    """ wrap silva.p node around text"""
    content = Frag()
    breaks = 'heading','p','list','nlist','table'

    pre, tag, post = container.find_and_partition(breaks)
    if pre:
        content.append(p(*pre))
    if tag:
        content.append(tag)
    if post:
        content.extend(mixin_paragraphs(post))
    return content

""" current mapping of silva
h1  :  not in use, reserved for (future) Silva publication
       sections and custom templates
h2  :  title
h3  :  heading
h4  :  subhead
h5  :  list title
"""
