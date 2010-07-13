# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from cgi import escape
from HTMLParser import HTMLParseError

from Products.Silva.silvaxml.xmlexport import (
    theXMLExporter, VersionedContentProducer, SilvaBaseProducer)
from Products.SilvaExternalSources.ExternalSource import getSourceForId
from Products.ParsedXML.DOM.Core import Node
from Products.SilvaDocument.i18n import translate as _
from Products.SilvaDocument import interfaces
from Products.SilvaDocument.silvaxml import NS_SILVA_DOCUMENT

from five import grok
from silva.core.interfaces import IImage
from silva.core.interfaces.adapters import IPath
from silva.core.references.interfaces import IReferenceService
from sprout.saxext.html2sax import saxify
from zope import component
from zope.interface import Interface
from zope.traversing.browser import absoluteURL


theXMLExporter.registerNamespace('doc', NS_SILVA_DOCUMENT)


class DocumentProducer(VersionedContentProducer):
    """Export a Silva Document object to XML.
    """
    grok.adapts(interfaces.IDocument, Interface)

    def sax(self):
        self.startElement('document', {'id': self.context.id})
        self.workflow()
        self.versions()
        self.endElement('document')


class DocumentVersionProducer(SilvaBaseProducer):
    """Export a version of a Silva Document object to XML.
    """
    grok.adapts(interfaces.IDocumentVersion, Interface)

    def sax(self):
        self.startElement('content', {'version_id': self.context.id})
        self.metadata()
        node = self.context.content.documentElement.getDOMObj()
        self.sax_node(node)
        self.endElement('content')

    def sax_node(self, node):
        """Export child nodes of a (version of a) Silva Document to XML
        """
        attributes = {}
        if node.attributes:
            attributes = get_dict(node.attributes)
        if node.nodeName == 'source':
            self.sax_source(node)
        elif node.nodeName == 'table':
            self.sax_table(node)
        elif node.nodeName == 'image':
            self.sax_img(node)
        else:
            if node.nodeName == 'link':
                settings = self.getSettings()
                if settings.externalRendering():
                    rewritten_url = ''
                    if 'reference' in attributes:
                        service = component.getUtility(IReferenceService)
                        reference = service.get_reference(
                            self.context, name=attributes['reference'])
                        rewritten_url = absoluteURL(
                            reference.target, settings.request)
                    elif 'url' in attributes:
                        document = self.context.get_content()
                        rewritten_url = IPath(document).pathToUrlPath(
                            attributes['url'])
                    anchor = attributes.get('anchor', '')
                    if anchor:
                        rewritten_url += '#' + anchor
                    attributes['rewritten_url'] = rewritten_url
                else:
                    if 'reference' in attributes:
                        attributes['reference'] = self.reference(
                            attributes['reference'])

            self.startElementNS(NS_SILVA_DOCUMENT, node.nodeName, attributes)
            if node.hasChildNodes():
                self.sax_children(node)
            elif node.nodeValue:
                self.handler.characters(node.nodeValue)
            self.endElementNS(NS_SILVA_DOCUMENT, node.nodeName)

    def sax_children(self, node):
        for child in node.childNodes:
            if child.nodeType == Node.TEXT_NODE:
                if child.nodeValue:
                    self.handler.characters(child.nodeValue)
            elif child.nodeType == Node.ELEMENT_NODE:
                self.sax_node(child)

    def sax_source(self, node):
        # simple output reporting to emulate behavior of widgets renderer
        def source_error(error):
            html = ['<div class="warning"><strong>[',
                    "external source element is broken",
                    ']</strong><br />',
                    escape(unicode(error)),
                    '</div>']
            self.render_html("".join(html))
            self.endElementNS(NS_SILVA_DOCUMENT, node.nodeName)

        attributes = {}
        if node.attributes:
            attributes = get_dict(node.attributes)
        self.startElementNS(NS_SILVA_DOCUMENT, node.nodeName, attributes)
        try:
            # this can happen if no source was specified when the
            # element was added
            id = attributes['id']
        except KeyError:
            source_error(_("no external source specified"))
            return
        source = getSourceForId(self.context.get_content(), id)
        parameters = {}
        for child in node.childNodes:
            if child.nodeName == 'parameter':
                attributes = {'key': child.attributes['key'].value}
                param_type = child.attributes.get('type')
                if param_type:
                    attributes['type'] = param_type.value
                self.startElementNS(NS_SILVA_DOCUMENT, 'parameter', attributes)
                for grandChild in child.childNodes:
                    text = ''
                    if grandChild.nodeType == Node.TEXT_NODE:
                        if grandChild.nodeValue:
                            self.handler.characters(grandChild.nodeValue)
                            text = text + grandChild.nodeValue
                    parameters[str(child.attributes['key'].value)] = text
                self.endElementNS(NS_SILVA_DOCUMENT, 'parameter')
        if self.getSettings().externalRendering():
            try:
                html = source.to_html(self.context, None, **parameters)
            except Exception, err:
                source_error(unicode(_("error message:")) + " " + str(err))
                return
            if not html:
                source_error(unicode(_("error message:")) + " " \
                                 + unicode(_("None returned from source")))
                return
            self.render_html(html)
        self.endElementNS(NS_SILVA_DOCUMENT, node.nodeName)

    def sax_table(self, node):
        attributes = {}
        if node.attributes:
            attributes = get_dict(node.attributes)
        self.startElementNS(NS_SILVA_DOCUMENT, 'table', attributes)
        columns_info = self.get_columns_info(node)
        nr_of_columns = len(columns_info)
        for column in columns_info:
            col_attributes = {'class': 'align-' + column['align']}
            width = column.get('html_width')
            if width:
                col_attributes['width'] = width
            self.startElementNS(NS_SILVA_DOCUMENT, 'col', col_attributes)
            self.endElementNS(NS_SILVA_DOCUMENT, 'col')
        if node.hasChildNodes():
            row = 0
            for child in node.childNodes:
                if child.nodeName == 'row_heading':
                    self.sax_row_heading(child, nr_of_columns)
                elif child.nodeName == 'row':
                    row += 1
                    self.sax_row(child, row, columns_info)
        self.endElementNS(NS_SILVA_DOCUMENT, 'table')

    def sax_row_heading(self, node, nr_of_columns):
        child_attrs = {'colspan': str(nr_of_columns)}
        self.startElementNS(NS_SILVA_DOCUMENT, 'row_heading', child_attrs)
        if node.hasChildNodes():
            self.sax_children(node)
        self.endElementNS(NS_SILVA_DOCUMENT, 'row_heading')

    def sax_row(self, node, row, columns_info):
        child_attrs = {'class': row % 2 and "odd" or "even"}
        self.startElementNS(NS_SILVA_DOCUMENT, 'row', child_attrs)
        if node.hasChildNodes:
            col = 0
            for child in node.childNodes:
                if child.nodeType == Node.ELEMENT_NODE:
                    self.sax_field(child, columns_info[col])
                    col += 1
        self.endElementNS(NS_SILVA_DOCUMENT, 'row')

    def sax_field(self, node, col_info):
        child_attrs = {'class': 'align-' + col_info['align'],
                       'fieldtype': node.getAttribute('fieldtype') or 'td'}
        if node.hasAttribute('colspan'):
            child_attrs['colspan'] = node.getAttribute('colspan')
        self.startElementNS(NS_SILVA_DOCUMENT, 'field', child_attrs)
        if node.hasChildNodes():
            for child in node.childNodes:
                if child.nodeType == Node.TEXT_NODE:
                    if child.nodeValue:
                        self.handler.characters(child.nodeValue)
                else:
                    # XXX UGLY EVIL HACK to make this behave the same as
                    # the widget renderer, i.e. remove the tags of the
                    # first child if it is a <p>
                    if child is node.firstChild and child.nodeName == 'p':
                        for grandchild in child.childNodes:
                            if grandchild.nodeType == Node.TEXT_NODE:
                                self.handler.characters(grandchild.nodeValue)
                            else:
                                if grandchild.nodeName == 'image':
                                    self.sax_img(grandchild)
                                else:
                                    self.sax_node(grandchild)
                    else:
                        if child.nodeName == 'image':
                            self.sax_img(child)
                        else:
                            self.sax_node(child)
        self.endElementNS(NS_SILVA_DOCUMENT, 'field')

    def get_columns_info(self, node):
        columns = int(node.getAttribute('columns'))
        if node.hasAttribute('column_info'):
            column_info = node.getAttribute('column_info')
        else:
            result = []
            for i in range(columns):
                result.append({'align': 'left', 'width': 1,
                               'html_width': '%s%%' % (100 / columns)})
            node.REQUEST.set('columns_info', result)
            return result

        lookup = {'L': 'left', 'C': 'center', 'R': 'right'}

        result = []
        for info in column_info.split():
            info = info.split(':')
            try:
                align = info[0]
            except IndexError:
                align = 'L'
            try:
                width = int(info[1])
            except IndexError:
                width = 0
            except ValueError:
                width = 0
            if width:
                info_dict = {
                    'align': lookup.get(align, 'L'),
                    'width': width}
            else:
                info_dict = {
                    'align': lookup.get(align, 'L')}
            result.append(info_dict)

        # too much info, ignore it
        if len(result) > columns:
            result = result[:columns]
        # not enough info, take average and add to missing columns
        elif len(result) < columns:
            total = 0
            for info in result:
                total += info.get('width', 0)
            average = total / len(result)
            if average > 0:
                for i in range(columns - len(result)):
                    result.append({'align': 'left', 'width': average})

        # calculate percentages
        total = 0
        for info in result:
            total += info.get('width', 0)
        for info in result:
            if info.get('width'):
                percentage = int((float(info['width']) / total) * 100)
                info['html_width'] = '%s%%' % percentage
        return result

    def sax_img(self, node):
        """Unfortunately <image> is a special case, since height and width
        are not stored in the document but in the Image object itself, and
        need to be retrieved here.
        """
        attributes = {}
        settings = self.getSettings()
        if node.attributes:
            attributes = get_dict(node.attributes)

        if settings.externalRendering():
            rewritten_path = None
            if 'reference' in attributes:
                service = component.getUtility(IReferenceService)
                reference = service.get_reference(
                    self.context, name=attributes['reference'])
                image = reference.target
                rewritten_path = image.absolute_url()
            else:
                document = self.context.get_content()
                image = document.unrestrictedTraverse(
                    attributes['path'].split('/'), None)
                rewritten_path = IPath(document).pathToUrlPath(
                    attributes['path'])
            attributes['rewritten_path'] = rewritten_path

            if image is not None:
                if IImage.providedBy(image):
                    image_res = settings.options.get('image_res', 'hires')
                    attributes['title'] = image.get_title()
                    width, height = image.getDimensions(image.image)
                    if image_res == 'hires':
                        attributes['width'] = str(width)
                        attributes['height'] = str(height)
                    attributes['rewritten_path'] += \
                        '?%s' % image_res
        else:
            if 'reference' in attributes:
                attributes['reference'] = self.reference(
                    attributes['reference'])

        if attributes.has_key('alignment'):
            if not attributes['alignment']:
                attributes['alignment'] = 'default'
        else:
            attributes['alignment'] = 'default'
        self.startElementNS(NS_SILVA_DOCUMENT, node.nodeName, attributes)
        self.endElementNS(NS_SILVA_DOCUMENT, node.nodeName)

    def render_html(self, html):
        self.startElementNS(NS_SILVA_DOCUMENT, 'rendered_html')
        try:
            # We don't trust that the input is even valid HTML.
            saxify(html, self.handler, validate=True)
        except HTMLParseError error:
            error_message = [
                '<div class="htmlerror">',
                '<strong>%s at line %d:%d in</strong>' % (
                    escape(error.msg), error.lineno, error.offset),
                '<pre>%s</pre></div>' % escape(html)]
            # Report the error message which is valid
            saxify("".join(error_message), self.handler)
        self.endElementNS(NS_SILVA_DOCUMENT, 'rendered_html')


def get_dict(attributes):
    result = {}
    for key in attributes.keys():
        result[key] = attributes[key].value
    return result
