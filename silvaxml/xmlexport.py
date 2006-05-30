from Products.Silva.silvaxml.xmlexport import theXMLExporter, VersionedContentProducer, SilvaBaseProducer
from sprout.saxext.html2sax import saxify
from Products.ParsedXML.DOM.Core import Node

SilvaDocumentNS = 'http://infrae.com/ns/silva_document'

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
            for key in node.attributes.keys():
                attributes[key] = node.attributes[key].value
        self.startElementNS(SilvaDocumentNS, node.nodeName, attributes)
        if node.nodeName == 'source' and node.parentNode.nodeName != 'cite': 	        
            self.sax_source(node, attributes['id'])
        elif node.nodeName == 'toc' and self.getSettings().externalRendering():
            self.sax_toc(node, attributes['toc_depth'])
        elif node.hasChildNodes():
            self.sax_children(node)
        else:
            if node.nodeValue:
                self.handler.characters(node.nodeValue)
        self.endElementNS(SilvaDocumentNS, node.nodeName)

    def sax_children(self, node):
        for child in node.childNodes:
            if child.nodeType == Node.TEXT_NODE:
                if child.nodeValue:
                    self.handler.characters(child.nodeValue)
            elif child.nodeType == Node.ELEMENT_NODE:
                if child.nodeName == 'table':
                    self.sax_table(child)
                elif child.nodeName == 'image':
                    self.sax_img(child)
                else:
                    self.sax_node(child)
        
    def sax_source(self, node, id): 	 
        try:
            from Products.SilvaExternalSources.ExternalSource import getSourceForId 	 
        except ImportError:
            return
        source = getSourceForId(self.context, id) 	 
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
            html = source.to_html(self.context.REQUEST, **parameters) 	 
            self.render_html(html)
             
    def sax_table(self, node):
        attributes = {}
        if node.attributes:
            for key in node.attributes.keys():
                attributes[key] = node.attributes[key].value
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
        
    def sax_toc(self, node, depth):
        # XXX hack to get the right context for the toc, in case we're
        # actually rendering a ghost. This probably will change (for the
        # better:) in Silva 1.2 or later.
        toc_context = self.context
        depth = int(depth)
        request = getattr(self.context, 'REQUEST', None)
        if request is not None:
            ghost_model = getattr(request, 'ghost_model', None)
            if ghost_model is not None:
                toc_context = ghost_model
        public = self.context.version_status() == 'public'
        if public:
            tree = toc_context.get_public_tree(depth)
            append_to_url = ''
        else:
            tree = toc_context.get_tree(depth)
            append_to_url = 'edit/tab_preview'
        text = ''
        for obj in tree:
            indent = obj[0]
            item = obj[1]
            if public:
                title = item.get_title()
            else:
                title = item.get_title_editable()
            url = item.absolute_url()
            if indent > 0:
                text = text + '<img width="%s" height="14" alt="" src="%s/globals/pixel.gif" />' % (
                    str(indent * 24),
                    self.context.REQUEST['BASE2']
                    )
            text = text + '<a href="%s/%s">%s</a><br />' % (
                url,
                append_to_url,
                title
                )
        html = '<p class="toc">%s</p>' % text
        self.render_html(html)

    def sax_img(self, node):
        """Unfortunately <image> is a special case, since height and width 
        are not stored in the document but in the Image object itself, and
        need to be retrieved here.
        """
        attributes = {}
        if node.attributes:
            for key in node.attributes.keys():
                attributes[key] = node.attributes[key].value
        image_object = self.context.get_silva_object().unrestrictedTraverse(
            attributes['path'].split('/'), None)
        if image_object is not None:
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
       
