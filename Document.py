# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Python
from StringIO import StringIO
import re
import sys
import traceback

# Zope
from zope import lifecycleevent
from zope.event import notify
from zope.interface import implements

from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from Persistence import Persistent
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from zExceptions import InternalError
import OFS.interfaces

from Products.ParsedXML.ParsedXML import ParsedXML

# Silva
from Products.Silva import SilvaPermissions
from Products.Silva.VersionedContent import CatalogedVersionedContent
from Products.Silva.Version import CatalogedVersion
from Products.Silva import mangle
from Products.Silva.helpers import translateCdata
from Products.Silva.ContentObjectFactoryRegistry import contentObjectFactoryRegistry

# Silva Document
from Products.SilvaDocument.transform.Transformer import EditorTransformer
from Products.SilvaDocument.transform.base import Context
from Products.SilvaDocument.interfaces import IDocument, IDocumentVersion
from Products.SilvaDocument.i18n import translate as _
from Products.SilvaDocument import externalsource

from Products.SilvaMetadata.Exceptions import BindingError

from silva.core import conf as silvaconf
from silva.core.interfaces import IContainerPolicy
from silva.core.smi.interfaces import IFormsEditorSupport, IKupuEditorSupport
from silva.core.views import views as silvaviews
from silva.core.views import z3cforms as silvaz3cforms

from z3c.form import field


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
    implements(IDocumentVersion)

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
            self.object().getId(),
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
            stream.write('<silva_document id="%s">' % self.object().getId())
            # Write Title
            stream.write('<title>%s</title>' % translateCdata(self.get_title()))

        # Write Document
        document = self._get_document_element()
        document.writeStream(stream)

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
    def set_document_xml_from(self, content, format='kupu', request=None):
        """Set the document xml of the version from the given content
        in the given format.
        """
        errors = self._set_metadata_from_content(content)
        if errors:
            raise ValueError(errors)

        transformer = EditorTransformer(editor=format)
        context = Context(self, request)

        document = transformer.to_source(targetobj=content, context=context)[0]
        title = document.find('title')[0].extract_text()
        content = document.find('doc')[0].asBytes(encoding="UTF8")
        self.content.manage_edit(content)
        self.set_title(title)

        notify(lifecycleevent.ObjectModifiedEvent(self))
        # Should be on event
        self.clear_editor_cache()

    def _set_metadata_from_content(self, html):
        """Rip the metadata out of the HTML (meta tags), set it on version"""
        # XXX obviously it would make sense if the transformations could
        # tackle this instead of doing it seperately, however, they are messy
        # enough as they are now (and not capable of such a thing yet)

        # XXX SAX took about 2 seconds (!) to get the meta values,
        # so I decided to try re instead... this made sense, parsing now takes
        # less than one hundreth of a second (usually even less than one
        # thousandth!)

        def _deentitize(xml):
            return xml.replace('&lt;', '<').replace('&gt;', '>').\
                replace('&quot;', '"').replace('&amp;', '&')

        mapping = {}
        reg = re.compile(r'\<meta[^\>]+\/\>')
        while 1:
            match = reg.search(html)
            if not match:
                break
            tag = match.group(0)
            html = html.replace(tag, '')
            reg_props = re.compile(r'([a-zA-Z_]+)="([^"]+)"')
            found = {}
            while 1:
                match = reg_props.search(tag)
                if not match:
                    break
                tag = tag.replace(match.group(0), '')
                if match.group(1) in ['name', 'content', 'scheme']:
                    found[match.group(1)] = _deentitize(match.group(2))
                if (found.has_key('name') and found.has_key('content') and
                        found.has_key('scheme')):
                    if not mapping.has_key(found['scheme']):
                        mapping[found['scheme']] = {}
                    mapping[found['scheme']][found['name']] = found['content']

        errors = {}
        binding = self.service_metadata.getMetadata(self)
        for namespace, values in mapping.items():
            # %!#$%# metadata system expects UTF-8 :(
            for key, value in values.items():
                del values[key]
                if value is None:
                    continue
                values[key.encode('UTF-8')] = value.encode('UTF-8')
            set = self.service_metadata.getMetadataSetFor(namespace)
            ret = binding.setValues(set.id, values, reindex=1)
            if ret:
                errors.update(ret)
        return errors

    def _get_document_element(self):
        """returns the document element of this
           version's ParsedXML object.
           This is abstracted so that objects which
           extend Document (e.g. News Items) can
           have a different xml implementation
           (i.e. silvaxmlattribute)"""
        return self.content.documentElement

    def clear_editor_cache(self):
        """ Clears editor cache for this version
        """
        try:
            self.editor_service.clearCache(self._get_document_element())
        except AttributeError:
            # This fail when you don't have a self.REQUEST. However
            # it's not a big deal, the entry will expire.
            pass

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

    implements(IDocument, IKupuEditorSupport, IFormsEditorSupport)

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
        for node in viewable._get_document_element().childNodes:
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

    def revert_to_previous(self):
        """ Create a new version of public version, throw away the
        current one.

        Overrides Versioning.revert_to_previous() to be able to clear
        the widget cache too.
        """
        super(Document, self).revert_to_previous()
        version = self.get_editable()
        version.clear_editor_cache()

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


class DocumentAddForm(silvaz3cforms.AddForm):
    """Add form for a document.
    """

    silvaconf.context(IDocument)
    silvaconf.name(u'Silva Document')
    fields = field.Fields(IDocumentVersion)


class DocumentView(silvaviews.View):
    """View on a document.
    """

    silvaconf.context(IDocument)

    def render(self):
        service_editor = self.context.service_editor
        service_editor.setViewer('service_doc_viewer')
        # For service_editor
        self.request['model'] = self.content
        return service_editor.renderView(self.content.content.documentElement)


@silvaconf.subscribe(IDocument, OFS.interfaces.IObjectWillBeRemovedEvent)
def document_will_be_removed(document, event):
    # Does the widget cache needs be cleared for all versions - I think so...
    # XXX reply to comment: that's not all the version you used (me neither)!
    version_ids = [
        document.get_next_version(),
        document.get_public_version(),]
    for version_id in version_ids:
        if version_id is None:
            continue
        if hasattr(document.aq_base, version_id):
            version = getattr(document, version_id)
            document.service_editor.clearCache(version.content)


@silvaconf.subscribe(IDocumentVersion, OFS.interfaces.IObjectClonedEvent)
def documentversion_cloned(documentversion, event):
    # if we're a copy, clear cache
    # XXX should be part of workflow system
    documentversion.clear_editor_cache()


class SilvaDocumentPolicy(Persistent):

    implements(IContainerPolicy)

    def createDefaultDocument(self, container, title):
        container.manage_addProduct['SilvaDocument'].manage_addDocument(
            'index', title)
        container.index.sec_update_last_author_info()

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

