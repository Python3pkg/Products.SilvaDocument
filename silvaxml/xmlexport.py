# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import re
from urlparse import urlparse
from Products.Silva.silvaxml.xmlexport import theXMLExporter, VersionedContentProducer, SilvaBaseProducer
from sprout.saxext.html2sax import saxify
from Products.ParsedXML.DOM.Core import Node
from Products.Silva.adapters.path import getPathAdapter
from Products.Silva.adapters import tocrendering
from Products.Silva.interfaces import IImage
from Products.SilvaDocument.i18n import translate as _

SilvaDocumentNS = 'http://infrae.com/ns/silva_document'
URL_PATTERN = r'(http://|https://|ftp://|news://|mailto:)+'
_url_match = re.compile(URL_PATTERN)

def initializeXMLExportRegistry():
    """Here the actual content types are registered. Non-Silva-Core content
    types probably need to register themselves in in their product
    __init__.pies
    """
    from Products.SilvaDocument.Document import Document, DocumentVersion
    exporter = theXMLExporter
    exporter.registerNamespace('doc', SilvaDocumentNS)
    exporter.registerProducer(Document, DocumentProducer)
    exporter.registerProducer(DocumentVersion, DocumentVersionProducer)


class DocumentProducer(VersionedContentProducer):
    """Export a Silva Document object to XML.
    """
    def sax(self):
        self.startElement('document', {'id': self.context.id})
        self.workflow()
        self.versions()
        self.endElement('document')

class DocumentVersionProducer(SilvaBaseProducer):
    """Export a version of a Silva Document object to XML.
    """
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
        if node.nodeName == 'source' and node.parentNode.nodeName != 'cite': 	        
            self.sax_source(node)
        elif node.nodeName == 'toc' and self.getSettings().externalRendering():
            self.sax_toc(node)
        elif node.nodeName == 'table':
            self.sax_table(node)
        elif node.nodeName == 'image':
            self.sax_img(node)
        else:
            if node.nodeName == 'link':
                attributes['rewritten_url'] = self.rewriteUrl(attributes['url'])
            self.startElementNS(SilvaDocumentNS, node.nodeName, attributes)
            if node.hasChildNodes():
                self.sax_children(node)
            elif node.nodeValue:
                self.handler.characters(node.nodeValue)
            self.endElementNS(SilvaDocumentNS, node.nodeName)

    def sax_children(self, node):
        for child in node.childNodes:
            if child.nodeType == Node.TEXT_NODE:
                if child.nodeValue:
                    self.handler.characters(child.nodeValue)
            elif child.nodeType == Node.ELEMENT_NODE:
                self.sax_node(child)
        
    def sax_source(self, node):
        #simple output reporting to emulate behavior of widgets renderer
        def source_error(thiserror):
            html = ['<div class="warning"><strong>[',
                    unicode(_("external source element is broken")),
                    ']</strong><br />',
                    thiserror,
                    '</div>']
            self.render_html("".join(html))
            self.endElementNS(SilvaDocumentNS, node.nodeName)
        attributes = {}
        if node.attributes:
            attributes = get_dict(node.attributes)
        self.startElementNS(SilvaDocumentNS, node.nodeName, attributes)
        try:
            from Products.SilvaExternalSources.ExternalSource import getSourceForId 	 
        except ImportError:
            source_error(unicode(_("external source element specified but silvaexternalsources not installed!")))
            return
        try: #this can happen if no source was specified when the element was added
            id = attributes['id']
        except KeyError:
            source_error(unicode(_("no external source specified")))
            return
        source = getSourceForId(self.context.get_content(), id)
        parameters = {} 	 
        for child in node.childNodes: 	 
            if child.nodeName == 'parameter': 	 
                self.startElementNS(SilvaDocumentNS, 'parameter', {'key': child.attributes['key'].value}) 	 
                for grandChild in child.childNodes: 	 
                    text = '' 	 
                    if grandChild.nodeType == Node.TEXT_NODE: 	 
                        if grandChild.nodeValue: 	 
                            self.handler.characters(grandChild.nodeValue)
                            text = text + grandChild.nodeValue
                    parameters[str(child.attributes['key'].value)] = text 	 
                self.endElementNS(SilvaDocumentNS, 'parameter')
        if self.getSettings().externalRendering():
            request = self.context.REQUEST
            request.set('model', self.context.aq_inner)
            try:
                html = source.to_html(request, **parameters)
            except Exception, err:
                if source and hasattr(source.aq_explicit,'log_traceback'):
                    source.log_traceback()
                source_error(unicode(_("error message:")) + " " + str(err))
                return
            if not html:
                source_error(unicode(_("error message:")) + " " + unicode(_("None returned from source")))
                return
            if not request.get('edit_mode', None):
                request.set('model', None)
            self.render_html(html)
        self.endElementNS(SilvaDocumentNS, node.nodeName)
             
    def sax_table(self, node):
        attributes = {}
        if node.attributes:
            attributes = get_dict(node.attributes)
        self.startElementNS(SilvaDocumentNS, 'table', attributes)
        columns_info = self.get_columns_info(node)
        nr_of_columns = len(columns_info)
        for column in columns_info:
            col_attributes = {'class': 'align-' + column['align']}
            width = column.get('html_width')
            if width:
                col_attributes['width'] = width
            self.startElementNS(SilvaDocumentNS, 'col' , col_attributes)
            self.endElementNS(SilvaDocumentNS, 'col')
        if node.hasChildNodes():
            row = 0
            for child in node.childNodes:
                if child.nodeName == 'row_heading':
                    self.sax_row_heading(child, nr_of_columns)
                elif child.nodeName == 'row':
                    row += 1
                    self.sax_row(child, row, columns_info)
        self.endElementNS(SilvaDocumentNS, 'table')

    def sax_row_heading(self, node, nr_of_columns):
        child_attrs = {'colspan': str(nr_of_columns)}
        self.startElementNS(SilvaDocumentNS, 'row_heading', child_attrs)
        if node.hasChildNodes():
            self.sax_children(node)
        self.endElementNS(SilvaDocumentNS, 'row_heading')
        
    def sax_row(self, node, row, columns_info):
        child_attrs = {'class': row % 2 and "odd" or "even"}
        self.startElementNS(SilvaDocumentNS, 'row', child_attrs)
        if node.hasChildNodes:
            col = 0
            for child in node.childNodes:
                if child.nodeType == Node.ELEMENT_NODE:
                    self.sax_field(child, columns_info[col])
                    col += 1
        self.endElementNS(SilvaDocumentNS, 'row')
        
    def sax_field(self, node, col_info):
        child_attrs = {'class': 'align-' + col_info['align']}
        self.startElementNS(SilvaDocumentNS, 'field', child_attrs)
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
        self.endElementNS(SilvaDocumentNS, 'field')
        
    def get_columns_info(self, node):
        columns = int(node.getAttribute('columns'))
        if node.hasAttribute('column_info'):
            column_info = node.getAttribute('column_info')
        else:
            result = []
            for i in range(columns):
                result.append({'align': 'left', 'width': 1, 'html_width':'%s%%' % (100/columns) })
            node.REQUEST.set('columns_info', result)
            return result

        lookup = { 'L':'left', 'C':'center', 'R': 'right' }
        
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
                    'width': width,
                    }
            else:
                info_dict = {
                    'align': lookup.get(align, 'L'),
                    }
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
                    result.append({'align': 'left', 'width': average })

        # calculate percentages
        total = 0
        for info in result:
            total += info.get('width', 0)
        for info in result:
            if info.get('width'):
                percentage = int((float(info['width'])/total) * 100)
                info['html_width'] = '%s%%' % percentage
        return result
        
    def sax_toc(self, node):
        attributes = {}
        if node.attributes:
            attributes = get_dict(node.attributes)
        self.startElementNS(SilvaDocumentNS, node.nodeName, attributes)
        # default depth of -1
        depth = attributes.get('toc_depth',-1)
        toc_context = self.context
        depth = int(depth)

        # hack to get the right context for the toc, in case we're
        # rendering a ghost. The toc in a ghosted document actually
        # renders a table of contents for the context of the ghost
        request = getattr(self.context, 'REQUEST', None)
        if request is not None:
            ghost_model = getattr(request, 'ghost_model', None)
            if ghost_model is not None:
                toc_context = ghost_model

        tocadapter = tocrendering.getTOCRenderingAdapter(toc_context)
        self.render_html(tocadapter.render_tree(depth))
        self.endElementNS(SilvaDocumentNS, node.nodeName)

    def sax_img(self, node):
        """Unfortunately <image> is a special case, since height and width 
        are not stored in the document but in the Image object itself, and
        need to be retrieved here.
        """
        attributes = {}
        if node.attributes:
            attributes = get_dict(node.attributes)
        image_object = self.context.get_silva_object().unrestrictedTraverse(
            attributes['path'].split('/'), None)
        attributes['rewritten_path'] = self.rewriteUrl(attributes['path'])
        if attributes.get('link_to_hires', '0') == '1':
            attributes[
                'rewritten_link'] = attributes[
                'rewritten_path'] + '?hires'
        elif attributes.has_key('link'):
            if attributes['link']:
                attributes['rewritten_link'] = self.rewriteUrl(
                    attributes['link'])
        if image_object is not None:
            if IImage.providedBy(image_object):
                image = image_object.image
                attributes['image_title'] = image_object.get_title()
                width, height = image_object.getDimensions(image)
                attributes['width'] = str(width)
                attributes['height'] = str(height)
        if attributes.has_key('alignment'):
            if not(attributes['alignment']):
                attributes['alignment'] = 'default'
        else:
            attributes['alignment'] = 'default'
        self.startElementNS(SilvaDocumentNS, node.nodeName, attributes)
        self.endElementNS(SilvaDocumentNS, node.nodeName)
        
    def render_html(self, html):
        self.startElementNS(SilvaDocumentNS, 'rendered_html')
        saxify(html, self.handler)
        self.endElementNS(SilvaDocumentNS, 'rendered_html')
       
    def rewriteUrl(self, path):
        # XXX: copied verbatim from widgetrenderer
        # If path is empty (can it be?), just return it
        if path == '':
            return path
        # If it is a url already, return it:
        if _url_match.match(path):
            return path
        # Is it a query of anchor fragment? If so, return it
        if path[0] in ['?', '#']:
            return self.context.object().absolute_url() + path
        # It is not an URL, query or anchor, so treat it as a path.
        # If it is a relative path, treat is as such:
        if not path.startswith('/'):
            container = self.context.get_container()
            return self.convertPath(container.absolute_url() + '/' + path)
        # If it is an absolute path, try to traverse it to
        # a Zope/Silva object and get the URL for that.
        splitpath = [p.encode('ascii','ignore') for p in path.split('/') ]
        obj = self.context.restrictedTraverse(splitpath, None)
        if obj is None:
            # Was not found, maybe the link is broken, but maybe it's just 
            # due to virtual hosting situations or whatever.
            return self.convertPath(path)
        if hasattr(obj.aq_base, 'absolute_url'):
            # There are some cases where the object we find 
            # does not have the absolute_url method.
            return self.convertPath(obj.absolute_url())
        # In all other cases:
        return self.convertPath(path)
    
    def convertPath(self, path):
        """convert URL paths to absolute physical ones"""
        if urlparse(path)[0]:
            return path
        # we have a path
        pad = getPathAdapter(self.context.REQUEST)
        return pad.urlToPath(path)
    
def get_dict(attributes):
    result = {}
    for key in attributes.keys():
        result[key] = attributes[key].value
    return result
