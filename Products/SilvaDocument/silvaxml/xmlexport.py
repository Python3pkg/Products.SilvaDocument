# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from HTMLParser import HTMLParseError
from cgi import escape
import urllib
import logging

from Products.SilvaExternalSources.ExternalSource import getSourceForId
from Products.ParsedXML.DOM.Core import Node
from Products.SilvaDocument.i18n import translate as _
from Products.SilvaDocument import interfaces
from Products.SilvaDocument.silvaxml import NS_DOCUMENT_URI
from Products.SilvaDocument.upgrader.utils import resolve_path
from Products.SilvaDocument.interfaces import IPath

from five import grok
from silva.core.interfaces import IImage
from silva.core.references.interfaces import IReferenceService
from silva.core.views.interfaces import IVirtualSite
from silva.core.xml import producers
from sprout.saxext.html2sax import saxify
from zope.component import getUtility
from zope.interface import Interface
from zope.intid.interfaces import IIntIds
from zope.traversing.browser import absoluteURL

logger = logging.getLogger('silva.old.document')


# Those fields trigger problems in the new version. Automatically
# rename them to _value.
RENAMED_FIELDS = {
    'content': 'content_value',
    'script': 'script_value'}


class DocumentProducer(producers.SilvaVersionedContentProducer):
    """Export a Silva Document object to XML.
    """
    grok.adapts(interfaces.IDocument, Interface)

    def sax(self):
        self.startElement('document', {'id': self.context.id})
        if not self.getOptions().upgrade30:
            self.sax_workflow()
        self.sax_versions()
        self.endElement('document')


class DocumentVersionProducer(producers.SilvaProducer):
    """Export a version of a Silva Document object to XML.
    """
    grok.adapts(interfaces.IDocumentVersion, Interface)

    def sax(self):
        self.startElement('content', {'version_id': self.context.id})
        if not self.getOptions().upgrade30:
            self.sax_metadata()
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
                options = self.getOptions()
                if options.external_rendering:
                    href = ''
                    if 'reference' in attributes:
                        service = getUtility(IReferenceService)
                        reference = service.get_reference(
                            self.context, name=attributes['reference'])
                        if options.upgrade30:
                            attributes['data-silva-target'] = str(reference.target_id)
                            attributes['data-silva-reference'] = reference.tags[1]
                            reference.tags[0] = u"body link"
                            reference._p_changed = True
                        else:
                            target = reference.target
                            if target is not None:
                                href = absoluteURL(
                                    reference.target,
                                    self.getExported().request)
                            else:
                                attributes['class'] = 'broken-link'
                    elif 'url' in attributes:
                        if options.upgrade30:
                            attributes['data-silva-url'] = attributes['url']
                        else:
                            document = self.context.get_content()
                            href = IPath(document).pathToUrlPath(attributes['url'])

                    anchor = attributes.get('anchor', '')
                    if anchor:
                        if options.upgrade30:
                            attributes['data-silva-anchor'] = anchor
                        else:
                            href += '#' + anchor
                    attributes['href'] = href
                else:
                    if 'reference' in attributes:
                        attributes['reference'] = self.get_reference(
                            attributes['reference'])

            self.startElementNS(NS_DOCUMENT_URI, node.nodeName, attributes)
            if node.hasChildNodes():
                self.sax_children(node)
            elif node.nodeValue:
                self.handler.characters(node.nodeValue)
            self.endElementNS(NS_DOCUMENT_URI, node.nodeName)

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
            html = ['<div class="warning">'
                    '<strong>[external source element is broken]</strong>',
                    '<br />',
                    escape(unicode(error)),
                    '</div>']
            self.render_html("".join(html))
            self.endElementNS(NS_DOCUMENT_URI, node.nodeName)

        options = self.getOptions()
        parameters = {}
        parameters_type = {}
        for child in node.childNodes:
            if child.nodeName == 'parameter':
                name = str(child.attributes['key'].value)
                if options.upgrade30 and name in RENAMED_FIELDS:
                    name = RENAMED_FIELDS[name]
                param_type = child.attributes.get('type')
                if param_type:
                    parameters_type[name]= str(param_type.value)
                for grandChild in child.childNodes:
                    text = ''
                    if grandChild.nodeType == Node.TEXT_NODE:
                        if grandChild.nodeValue:
                            text = text + grandChild.nodeValue
                    parameters[name] = text

        attributes = {}
        if node.attributes:
            attributes = get_dict(node.attributes)

        try:
            id = attributes['id']
        except KeyError:
            return
        source = getSourceForId(self.context.get_content(), id)

        if options.upgrade30:

            if source is None:
                logger.error(u"Missing source %s, skipping it.", id)
                return
            logger.info(u'Document uses source %s.', id)

            value_settings = []
            seen_fields = set()

            def convert_parameter(name, value):
                field = source.parameters.get_field(name)
                value_settings.append(('marker_field_' + name, '1'))
                value_settings.append(('field_' + name + '_novalidate', '1'))
                if field.meta_type == 'ReferenceField':
                    content = self.context.get_content()
                    content_path = '/'.join(content.getPhysicalPath())
                    to_identifier = getUtility(IIntIds).register

                    def resolve_location(location):
                        url, target, fragment = resolve_path(
                            location, content_path, content, 'code source')
                        if target is not None:
                            value_settings.append(
                                ('field_' + name,
                                 str(to_identifier(target))))

                    is_multiple = field.get_value('multiple')
                    if is_multiple:
                        map(resolve_location, value.split(','))
                    else:
                        resolve_location(value)
                else:
                    parameter_type = parameters_type.get(name)
                    if parameter_type == 'boolean' or isinstance(value, bool):
                        if value in (True, u'1', u'True'):
                            value = u'1'
                        else:
                            # False boolean are not included in the settings.
                            return
                    if parameter_type == 'list' or isinstance(value, list):
                        if isinstance(value, basestring):
                            value = eval(value)
                        for item in value:
                            value_settings.append(
                                ('field_' + name,
                                 unicode(item).encode('utf-8')),)
                    else:
                        value_settings.append(
                            ('field_' + name,
                             unicode(value).encode('utf-8')),)

            if source.parameters is not None:
                # Convert actual stored value
                for name, value in parameters.items():
                    try:
                        convert_parameter(name, value)
                        seen_fields.add(name)
                    except AttributeError:
                        logger.error(
                            u"Parameter %s missing in source %s." % (
                                name, id))

                # For any field that was not seen, add the (required)
                # default value
                for field in source.parameters.get_fields():
                    if field.id not in seen_fields:
                        default_value = field.get_value('default')
                        if default_value is not None:
                            logger.warn(
                                u"Using default for parameter %s in source %s." % (
                                    field.id, id))
                            convert_parameter(field.id, default_value)

            attributes['settings'] = urllib.urlencode(value_settings)

        self.startElementNS(NS_DOCUMENT_URI, node.nodeName, attributes)

        if not options.upgrade30:
            # We don't need to include anything inside a code for the
            # upgrade, and don't need to render it.

            # Collect parameters
            for child in node.childNodes:
                if child.nodeName == 'parameter':
                    attributes = {'key': child.attributes['key'].value}
                    param_type = child.attributes.get('type')
                    if param_type:
                        attributes['type'] = param_type.value
                    self.startElementNS(NS_DOCUMENT_URI, 'parameter', attributes)
                    for grandChild in child.childNodes:
                        if grandChild.nodeType == Node.TEXT_NODE:
                            if grandChild.nodeValue:
                                self.handler.characters(grandChild.nodeValue)
                    self.endElementNS(NS_DOCUMENT_URI, 'parameter')

            # Render source if needed
            if options.external_rendering:
                request = self.getExported().request
                try:
                    html = source.to_html(self.context, request, **parameters)
                except Exception, error:
                    source_error("error message: " + str(error))
                    return
                if not html:
                    source_error("error message: the source returned no output.")
                    return
                self.render_html(html)

        self.endElementNS(NS_DOCUMENT_URI, node.nodeName)

    def sax_table(self, node):
        attributes = {}
        if node.attributes:
            attributes = get_dict(node.attributes)
        self.startElementNS(NS_DOCUMENT_URI, 'table', attributes)
        columns_info = self.get_columns_info(node)
        nr_of_columns = len(columns_info)
        for column in columns_info:
            col_attributes = {'class': 'align-' + column['align']}
            width = column.get('html_width')
            if width:
                col_attributes['width'] = width
            self.startElementNS(NS_DOCUMENT_URI, 'col', col_attributes)
            self.endElementNS(NS_DOCUMENT_URI, 'col')
        if node.hasChildNodes():
            row = 0
            for child in node.childNodes:
                if child.nodeName == 'row_heading':
                    self.sax_row_heading(child, nr_of_columns)
                elif child.nodeName == 'row':
                    row += 1
                    self.sax_row(child, row, columns_info)
        self.endElementNS(NS_DOCUMENT_URI, 'table')

    def sax_row_heading(self, node, nr_of_columns):
        child_attrs = {'colspan': str(nr_of_columns)}
        self.startElementNS(NS_DOCUMENT_URI, 'row_heading', child_attrs)
        if node.hasChildNodes():
            self.sax_children(node)
        self.endElementNS(NS_DOCUMENT_URI, 'row_heading')

    def sax_row(self, node, row, columns_info):
        child_attrs = {'class': row % 2 and "odd" or "even"}
        self.startElementNS(NS_DOCUMENT_URI, 'row', child_attrs)
        if node.hasChildNodes:
            col = 0
            for child in node.childNodes:
                if child.nodeType == Node.ELEMENT_NODE:
                    column_info = {'align': 'L'}
                    if len(columns_info) < col:
                        column_info = columns_info[col]
                    self.sax_field(child, column_info)
                    col += 1
        self.endElementNS(NS_DOCUMENT_URI, 'row')

    def sax_field(self, node, col_info):
        child_attrs = {'class': 'align-' + col_info['align'],
                       'fieldtype': node.getAttribute('fieldtype') or 'td'}
        if node.hasAttribute('colspan'):
            child_attrs['colspan'] = node.getAttribute('colspan')
        self.startElementNS(NS_DOCUMENT_URI, 'field', child_attrs)
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
        self.endElementNS(NS_DOCUMENT_URI, 'field')

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
        options = self.getOptions()
        request = self.getExported().request
        if node.attributes:
            attributes = get_dict(node.attributes)

        if options.external_rendering:
            rewritten_path = None
            if 'reference' in attributes:
                service = getUtility(IReferenceService)
                reference = service.get_reference(
                    self.context, name=attributes['reference'])
                image = reference.target
                if options.upgrade30:
                    attributes['data-silva-target'] = str(reference.target_id)
                    attributes['data-silva-reference'] = reference.tags[1]
                    reference.tags[0] = u"body image"
                    reference._p_changed = True
                elif image is not None:
                    rewritten_path = absoluteURL(image, request)
            else:
                document = self.context.get_content()
                image = document.unrestrictedTraverse(
                    attributes['path'].split('/'), None)
                if options.upgrade30:
                    attributes['data-silva-url'] = attributes['path']
                elif image is not None:
                    path = IPath(document)
                    rewritten_path = path.pathToUrlPath(attributes['path'])
            if not options.upgrade30:
                if not rewritten_path:
                    site = IVirtualSite(request)
                    rewritten_path = site.get_root_url() + \
                        "/++resource++Products.SilvaDocument/broken-link.jpg"
                    attributes['title'] = _(u'Referenced image is missing')
                attributes['rewritten_path'] = rewritten_path

            if image is not None:
                if IImage.providedBy(image):
                    resolution = options.image_res
                    attributes['title'] = image.get_title()
                    if resolution and not options.upgrade30:
                        attributes['rewritten_path'] += '?%s' % resolution
                        if resolution == 'hires':
                            width, height = image.get_dimensions()
                        attributes['width'] = str(width)
                        attributes['height'] = str(height)

        else:
            if 'reference' in attributes:
                attributes['reference'] = self.get_reference(
                    attributes['reference'])

        if attributes.has_key('alignment'):
            if not attributes['alignment']:
                attributes['alignment'] = 'default'
        else:
            attributes['alignment'] = 'default'
        self.startElementNS(NS_DOCUMENT_URI, node.nodeName, attributes)
        self.endElementNS(NS_DOCUMENT_URI, node.nodeName)

    def render_html(self, html):
        self.startElementNS(NS_DOCUMENT_URI, 'rendered_html')
        try:
            # We don't trust that the input is even valid HTML.
            saxify(html, self.handler, validate=True)
        except HTMLParseError, error:
            lined_html = ''
            for lineno, line in enumerate(escape(html).split('\n')):
                lined_html += 'line %03d: %s\n' % (lineno + 1, line)
            error_message = [
                '<div class="warning">',
                '<strong>external source generated invalid HTML:',
                ' %s at line %d:%d in</strong><br />' % (
                    escape(error.msg), error.lineno, error.offset),
                '<pre>%s</pre></div>' % lined_html]
            # Report the error message which is valid
            saxify("".join(error_message), self.handler)
        self.endElementNS(NS_DOCUMENT_URI, 'rendered_html')


def get_dict(attributes):
    result = {}
    for key in attributes.keys():
        result[key] = attributes[key].value
    return result
