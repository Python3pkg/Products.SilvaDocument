# -*- coding: utf-8 -*-
# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Python
from StringIO import StringIO
import re

# Zope
from five import grok
from zope import lifecycleevent
from zope.event import notify

from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from Persistence import Persistent
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from zExceptions import InternalError

from Products.ParsedXML.ParsedXML import ParsedXML

# Silva
from Products.Silva import SilvaPermissions
from Products.Silva.VersionedContent import CatalogedVersionedContent
from Products.Silva.Version import CatalogedVersion
from Products.Silva import mangle
from Products.Silva.helpers import translateCdata
from Products.Silva.ContentObjectFactoryRegistry import \
    contentObjectFactoryRegistry
from Products.Silva.transform.renderer.xsltrendererbase import XSLTTransformer

# Silva Document
from Products.SilvaDocument.transform.Transformer import EditorTransformer
from Products.SilvaDocument.transform.base import Context
from Products.SilvaDocument.interfaces import IDocument, IDocumentVersion
from Products.SilvaDocument.i18n import translate as _
from Products.SilvaDocument import externalsource

from silva.core import conf as silvaconf
from silva.core.interfaces import IContainerPolicy
from silva.core.views import views as silvaviews
from zeam.form import silva as silvaforms



def remove_source_xml(xml):
    """Remove code source source tag from the given XML as they may
    contain parameters with sensitive data, like password.
    """
    match = re.compile(
        r'<source id=".*?">.*?</source>', re.DOTALL|re.MULTILINE)
    xml = match.sub('', xml)
    return re.sub('<[^>]*>(?i)(?m)', ' ', xml)


class DocumentVersion(CatalogedVersion):
    """Silva Document version.
    """
    meta_type = "Silva Document Version"
    grok.implements(IDocumentVersion)

    security = ClassSecurityInfo()

    manage_options = (
        {'label':'Edit',       'action':'manage_main'},
        ) + CatalogedVersion.manage_options

    def __init__(self, id):
        super(DocumentVersion, self).__init__(id)
        self.content = ParsedXML('content', '<doc></doc>')

    # display edit screen as main management screen
    security.declareProtected('View management screens', 'manage_main')
    manage_main = PageTemplateFile('www/documentVersionEdit', globals())

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'fulltext')
    def fulltext(self):
        """Return the content of this object without any xml"""
        if self.version_status() == 'unapproved':
            return ''
        return [
            self.get_content().getId(),
            self.get_title(),
            remove_source_xml(self.get_document_xml(text_only=True))]

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'get_document_xml')
    def get_document_xml(self, text_only=False):
        """Generate a version of the document XML. You can restrict to
        only the text XML.
        """
        stream = StringIO()
        if not text_only:
            stream.write(
                '<silva_document id="%s">' % self.get_content().getId())
            # Write Title
            stream.write('<title>%s</title>' % translateCdata(self.get_title()))

        # Write Document
        self.content.documentElement.writeStream(stream)

        if not text_only:
            # Write Metadata
            binding = self.service_metadata.getMetadata(self)
            stream.write(binding.renderXML())
            # End of document
            stream.write('</silva_document>')

        return stream.getvalue()

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'get_document_xml_as')
    def get_document_xml_as(self, format='kupu', request=None):
        """Render the Document XML on a different format.
        """
        transformer = EditorTransformer(editor=format)
        context = Context(self, request)

        rendered_document = transformer.to_target(
            sourceobj=self.get_document_xml(), context=context)

        result = unicode(rendered_document.asBytes('utf8'), 'utf8')
        result = result.replace(u'\xa0', u'&nbsp;')
        return result

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_document_xml_from')
    def set_document_xml_from(self, data, format='kupu', request=None):
        """Set the document xml of the version from the given data
        in the given format.
        """
        transformer = EditorTransformer(editor=format)
        context = Context(self, request)

        document = transformer.to_source(targetobj=data, context=context)[0]
        title = document.find('title')[0].extract_text()
        content = document.find('doc')[0].asBytes(encoding="UTF8")
        self.content.manage_edit(content)
        self.set_title(title)

        notify(lifecycleevent.ObjectModifiedEvent(self))


InitializeClass(DocumentVersion)


class Document(CatalogedVersionedContent):
    __doc__ = _(
    """A Document is the basic unit of information in Silva. A document
        can &#8211; much like word processor documents &#8211; contain text,
        lists, tables, headers, subheads, images, etc. Documents can have
        two accessible versions, one online for the public, another in
        process (editable or approved/published). Older versions can be rolled
        forward and made editable.
    """)
    security = ClassSecurityInfo()

    meta_type = "Silva Document"

    grok.implements(IDocument)

    silvaconf.icon('www/silvadoc.gif')
    silvaconf.priority(-6)
    silvaconf.versionClass(DocumentVersion)

    # ACCESSORS
    security.declareProtected(SilvaPermissions.View, 'is_cacheable')
    def is_cacheable(self):
        """Return true if this document is cacheable.
        That means the document contains no dynamic elements like
        code, datasource or toc.
        """
        non_cacheable_elements = ['code',]

        viewable = self.get_viewable()
        if viewable is None:
            return 0

        # It should suffice to test the children of the root element only,
        # since currently the only non-cacheable elements are root elements
        for node in viewable.content.documentElement.childNodes:
            node_name = node.nodeName
            if node_name in non_cacheable_elements:
                return 0
            # FIXME: how can we make this more generic as it is very
            # specific now..?
            if node_name == 'source':
                is_cacheable = externalsource.isSourceCacheable(
                    self.aq_inner, node)
                if not is_cacheable:
                    return 0
        return 1

    # Kupu save doing a PUT
    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'PUT')
    def PUT(self, REQUEST=None, RESPONSE=None):
        """PUT support"""
        # XXX we may want to make this more modular/pluggable at some point
        # to allow more content-types (+ transformations)
        if REQUEST is None:
            REQUEST = self.REQUEST
        if RESPONSE is None:
            RESPONSE = REQUEST.RESPONSE
        editable = self.get_editable()
        if editable is None:
            raise InternalError('No editable version available')
        content = REQUEST['BODYFILE'].read()
        content_type = self._get_content_type_from_request(REQUEST, content)
        if content_type not in ['text/html', 'application/xhtml+xml']:
            raise InternalError('Input format not supported')
        editable.set_document_xml_from(content, request=REQUEST)

    def _get_content_type_from_request(self, request, content):
        """tries to figure out the content type of a PUT body from a request

            the request may not have a content-type header available, if so
            we should use the contents itself to determine the content type
        """
        content_type = request.get_header('content-type')
        if content_type is not None:
            return content_type.split(';')[0]
        content = re.sub('<?.*?>', '', content).strip()
        if content.startswith('<html') or content.startswith('<!DOCTYPE html'):
            return 'text/html'
        return 'application/x-silva-document-xml'


InitializeClass(Document)


class DocumentAddForm(silvaforms.SMIAddForm):
    """Add form for a document.
    """
    grok.context(IDocument)
    grok.name(u'Silva Document')

    description = Document.__doc__


DocumentHTML = XSLTTransformer('document.xslt', __file__)

class DocumentView(silvaviews.View):
    """View on a document.
    """
    grok.context(IDocument)

    def render(self):
        return DocumentHTML.transform(self.content, self.request)


class SilvaDocumentPolicy(Persistent):

    grok.implements(IContainerPolicy)

    def createDefaultDocument(self, container, title):
        factory = container.manage_addProduct['SilvaDocument']
        factory.manage_addDocument('index', title)


def document_factory(self, id, title, body):
    """Add a Document."""
    if not mangle.Id(self, id).isValid():
        return
    obj = Document(id).__of__(self)
    version = DocumentVersion('0').__of__(self)
    obj._setObject('0', version)
    obj.create_version('0', None, None)
    version = obj.get_editable()
    version.content.manage_edit(body)

    return obj

def _should_create_document(id, ct, body):
    rightct = (ct in ['application/x-silva-document-xml'])
    rightext = id.endswith('.slv')
    return rightct or rightext

contentObjectFactoryRegistry.registerFactory(
    document_factory,
    _should_create_document)

