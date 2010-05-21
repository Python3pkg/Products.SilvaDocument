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
__version__='$Revision: 1.26 $'

from Products.SilvaDocument.transform.base import Element, Frag, Text, \
    CharacterData

from zope.traversing.browser import absoluteURL
from Products.SilvaDocument.externalsource import getSourceForId
from silva.core.interfaces import IPath, IImage

import operator
import types
from urlparse import urlparse

import htmlformat
html = htmlformat

from silva.translations import translate as _


_attr_origin=u'silva_origin'
_attr_prefix=u'silva_'

# special attribute used for heuristics when transforming
# back to silva-xml

def xml_unescape(input):
    """de-entitize illegal chars in xml"""
    input = input.replace('&amp;', '&')
    input = input.replace('&lt;', '<')
    input = input.replace('&gt;', '>')
    return input


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
                    silva_id=self.attr.id,),
            node_body.convert(context),
            self.backattr(),
            class_='editor')
        return body

    def asBytes(self, *args, **kwargs):
        return SilvaElement.asBytes(self, *args, **kwargs)

class title(SilvaElement):
    """ us used with documents, list and tables (i guess) """

class doc(SilvaElement):
    """ subtag of silva_document """
    def asBytes(self, *args, **kwargs):
        # disabled xmlns declaration for now, should be solved properly later
        # self.attr.xmlns = 'http://xml.infrae.com/document/0.9.3'
        return SilvaElement.asBytes(self, *args, **kwargs)

class heading(SilvaElement):
    def convert(self, context):
        # some defensive programming here...
        level = self.attr.type
        h_tag = {u'normal' : html.h3,
                 u'sub': html.h4,
                 u'subsub': html.h5,
                 u'paragraph': html.h6,
                 u'subparagraph': html.h6,
                 }.get(level, html.h3)

        silva_type = None
        class_ = None
        if level == 'subparagraph':
            silva_type = 'sub'
            class_ = 'sub'

        return h_tag(
            self.content.convert(context),
            silva_type = silva_type,
            class_ = class_,
            )

class p(SilvaElement):
    def convert(self, context):
        ptype = self.getattr('type', 'normal')
        return html.p(
            self.content.convert(context),
            class_=ptype
            )

class br(Element):
    def convert(self, context):
        return html.br()

class list(SilvaElement):
    """ Simple lists """
    def convert(self, context):
        listtype = self.getattr('type', u'none')

        attrs = {}
        if listtype in ['1','i','I','a','A']:
            tag = html.ol
            attrs[u'type']=listtype
        elif listtype in (u'disc',u'square',u'circle'):
            tag = html.ul
        else:
            tag = html.ul

        # find nested lists, convert them to children of ourselves rather than
        # list items
        converted = []
        for child in self.find():
            if child.name() == 'li':
                sub = []
                for subchild in child.find():
                    if subchild.name() in ('list', 'nlist'):
                        # nested list, move out of li
                        child.content.remove(subchild)
                        sub.append(subchild.convert(context))
                    elif subchild.name() != 'br':
                        if sub and sub[-1].name() == 'li':
                            # additional subchild can contain other tags..
                            # add these to the previously added li 
                            # (f.e. a listitem with bold and linked words)
                            sub[-1].content.append(subchild.convert(context))
                        else:
                            # add *first* subchild content in li
                            sub.append(html.li(subchild.convert(context)))
                converted += sub
            else:
                converted.append(child.convert(context))
        return tag(
            converted,
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

class dlist(SilvaElement):
    def convert(self, context):
        children = []
        lastchild = None
        for child in self.find():
            if child.name() == 'dt':
                if lastchild is not None and lastchild.name() == 'dt':
                    children.append(html.dd(Text(' ')))
                children.append(html.dt(child.content.convert(context)))
                lastchild = child
            elif child.name() == 'dd':
                if lastchild is not None and lastchild.name() == 'dd':
                    children.append(html.dt(Text(' ')))
                children.append(html.dd(child.content.convert(context)))
                lastchild = child
        return html.dl(Frag(children))

class dt(SilvaElement):
    def convert(self, context):
        return html.dt(self.content.convert(context))

class dd(SilvaElement):
    def convert(self, context):
        return html.dd(self.content.convert(context))

class strong(SilvaElement):
    def convert(self, context):
        if context.browser == 'Mozilla':
            return html.b(self.content.convert(context))
        else:
            return html.strong(self.content.convert(context))

class underline(SilvaElement):
    def convert(self, context):
        return html.u(
            self.content.convert(context)
            )

class em(SilvaElement):
    def convert(self, context):
        if context.browser == 'Mozilla':
            return html.i(self.content.convert(context))
        else:
            return html.em(self.content.convert(context))

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
        title = self.getattr('title', None)
        target = self.getattr('target', None)
        anchor = self.getattr('anchor', None)

        if self.hasattr('reference'):
            # We have a reference
            reference_name = str(self.getattr('reference'))
            reference_name, reference = context.get_reference(reference_name)
            assert reference is not None, "Invalid reference"
            return html.a(
                self.content.convert(context),
                href='reference',
                title=title,
                target=target,
                silva_anchor=anchor,
                silva_target=reference.target_id,
                silva_reference=reference_name)

        path = self.getattr('url')
        if not urlparse(unicode(path))[0]:
            # path, not a full URL
            path = IPath(context.request).pathToUrlPath(unicode(path))
        return html.a(
            self.content.convert(context),
            href=path,
            silva_href=path,
            title=title,
            target=target,
            silva_anchor=anchor)


class index(SilvaElement):
    def convert(self, context):
        name = self.attr.name
        title = self.attr.title
        if title:
            title = unicode(self.attr.title.asBytes('utf-8'), 'utf-8')
        else:
            title = ''
        if title:
            text = Text('[#%s: %s]' % (name, title))
        else:
            text = Text('[#%s]' % name)
        return html.a(
            text,
            name=name,
            title=title,
            class_='index',)


class image(SilvaElement):

    def convert(self, context):
        image = None
        attributes = {'alignment': self.getattr('alignment', 'default'),
                      'alt': self.getattr('title', '')}

        if self.hasattr('reference'):
            # We have a reference
            reference_name = str(self.getattr('reference'))
            reference_name, reference = context.get_reference(reference_name)
            assert reference is not None, "Invalid reference"
            attributes['silva_target'] = reference.target_id
            attributes['silva_reference'] = reference_name
            image = reference.target
            attributes['src'] = absoluteURL(image, context.request)
        elif self.hasattr('path'):
            src = self.getattr('path')
            src = IPath(context.request).pathToUrlPath(str(src))
            attributes['src'] = src
            try:
                image = context.model.unrestrictedTraverse(src.split('/'))
            except:
                pass
        else:
            raise ValueError('Invalid silva image tag')

        if image and IImage.providedBy(image):
            attributes['width'], attributes['height'] = \
                image.getDimensions(image.image)

        return html.img(self.content.convert(context), **attributes)


class pre(SilvaElement):
    def compact(self):
        return self

    def convert(self, context):
        return html.pre(
            self.content.convert(context),)


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
        aligns = [(self.alignmapping.has_key(i[0]) and
                        self.alignmapping[i[0]] or 'left')
                    for i in infos]
        try:
            relwidths = [int(i[2:]) for i in infos]
        except ValueError:
            return ([], [])
        return aligns, relwidths


class row(SilvaElement):
    def convert(self, context):
        relwidths = context.tablestack[-1].relwidths
        if not hasattr(context.tablestack[-1], 'row_count'):
            context.tablestack[-1].row_count = 1
        else:
            context.tablestack[-1].row_count += 1

        widths = []
        if relwidths:
            reduced = reduce(operator.add, relwidths)
            if not reduced: #set it to 100 if all relwidths are 0
                reduced = 100
            units = 100 / reduced
            widths = [units * i for i in relwidths]
        aligns = context.tablestack[-1].aligns
        cells = self.find('field')
        if cells:
            for i in range(len(cells)):
                # leave some room for errors
                try:
                    cells[i].attr.align = aligns[i]
                    cells[i].attr.width = '%s%%' % int(widths[i])
                except (IndexError, ValueError):
                    cells[i].attr.align = 'left'
                    cells[i].attr.width = ''
        tr = html.tr(
            self.content.convert(context),
        )
        tr.attr.class_ = context.tablestack[-1].row_count % 2 and "odd" or "even"
        return tr

class row_heading(SilvaElement):
    def convert(self, context):
        cols = context.tablestack[-1].cols
        return html.tr(
            html.th(
                self.content.convert(context),
                colspan = str(cols)))


class field(SilvaElement):
    def convert(self, context):
        ft = getattr(self.attr,'fieldtype','td')
        c = ft=='td' and html.td or html.th
        kw = {'align':self.attr.align,
              'class_':'align-%s' % self.attr.align,
              'width':self.attr.width}
        colspan = getattr(self.attr,'colspan',None)
        if colspan:
            kw['colspan'] = colspan
        return c(
            self.content.convert(context), **kw)


class source(SilvaElement):

    def convert(self, context):
        # external source element
        id = self.attr.id
        params = {}
        attrparams = {}
        divcontent = []
        source = getSourceForId(context.model, str(id))
        if source is not None:
            meta_type = source.meta_type
            source_title = source.get_title() or id
            source_form = source.form()
            header = html.h4(Text(u'%s \xab%s\xbb' % (meta_type, source_title)),
                             title=u'source id: %s'%id)
            desc = source.description()
            if desc:
                divcontent.append(
                    html.p(desc, class_="externalsource-description"))
        else:
            source_title = ''
            source_form = None
            header = html.h4(
                Text('[%s]' % _('external source element is broken')))
        for child in self.find():
            if child.name() == 'parameter':
                vtype = child.getattr('type', 'string').convert(context).extract_text()
                value = child.content.convert(context).asBytes('utf-8')
                key = child.attr.key.convert(context).extract_text()
                attrkey = '%s__type__%s' % (key,vtype)
                if vtype == 'list':
                    value = [unicode(x, 'utf-8') for x in eval(value)]
                else:
                    value = unicode(value, 'utf-8')
                params[key] = (value,attrkey)
        divpar = []
        for key in params:
            value, attrkey = params[key]
            display_key = key
            if source_form is not None:
                try:
                    display_key = source_form.get_field(key).title()
                except AttributeError:
                    pass        # Field is gone

            divpar.append(html.strong("%s: " % display_key))
            if '__type__list' in attrkey:
                for v in value:
                    divpar.append(html.span(
                            Text(xml_unescape(v)), {'key': attrkey}))
                    divpar.append(Text(', '))
                divpar.pop()
            else:
                divpar.append(html.span(
                        Text(xml_unescape(value)), {'key': attrkey}))
            divpar.append(html.br());
        par = html.div(Frag(divpar), {'class': 'parameters'})
        divcontent.append(par)

        content = Frag(header, divcontent);
        return html.div(content,
                        source_id=id,
                        source_title = source_title,
                        class_='externalsource',
                        **attrparams)


class parameter(SilvaElement):
    def convert(self):
        return Frag()


class abbr(SilvaElement):
    def convert(self, context):
        return html.abbr(
            self.content.convert(context),
            title=self.attr.title)


class acronym(SilvaElement):
    def convert(self, context):
        return html.acronym(
            self.content.convert(context),
            title=self.attr.title)


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
