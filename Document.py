# Copyright (c) 2002-2004 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.23 $
# Zope

from StringIO import StringIO

from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Globals import InitializeClass
from Persistence import Persistent

from Products.ParsedXML.ExtraDOM import writeStream
from Products.ParsedXML.ParsedXML import createDOMDocument
from Products.ParsedXML.PrettyPrinter import _translateCdata
from Products.ParsedXML.ParsedXML import ParsedXML

# Silva
from Products.Silva import SilvaPermissions
from Products.Silva.VersionedContent import CatalogedVersionedContent
from Products.Silva.helpers import add_and_edit, translateCdata
from Products.Silva.Version import CatalogedVersion
from Products.Silva import mangle

from Products.Silva.ImporterRegistry import importer_registry, xml_import_helper, get_xml_id, get_xml_title
from Products.Silva.Metadata import export_metadata

# For XML-Conversions for editors
from transform.Transformer import EditorTransformer
from transform.base import Context

from Products.Silva.interfaces import IVersionedContent, IContainerPolicy
from Products.Silva.interfaces import IVersion

from Products.SilvaDocument import externalsource

icon="www/silvadoc.gif"
addable_priority = -1

class Document(CatalogedVersionedContent):
    """A Document is the basic unit of information in Silva. A document
        can -  much like word processor documents - contain text,
        lists, tables, headers, subheads, images, etc. Documents can have
        two (accessible) versions, one online for the public, another in
        process (editable or approved).
    """
    security = ClassSecurityInfo()

    meta_type = "Silva Document"

    __implements__ = IVersionedContent

    # A hackish way, to get a Silva tab in between the standard ZMI tabs
    inherited_manage_options = CatalogedVersionedContent.manage_options
    manage_options=(
        (inherited_manage_options[0],)+
        ({'label':'Silva /edit...', 'action':'edit'},)+
        inherited_manage_options[1:]
        )

    # ACCESSORS
    security.declareProtected(SilvaPermissions.View, 'is_cacheable')
    def is_cacheable(self):
        """Return true if this document is cacheable.
        That means the document contains no dynamic elements like
        code, datasource or toc.
        """
        non_cacheable_elements = ['toc', 'code', 'externaldata', ]

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

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'to_xml')
    def to_xml(self, context):
        """Render object to XML.
        """
        f = context.f

        if context.last_version == 1:
            version_id = self.get_next_version()
            if version_id is None:
                version_id = self.get_public_version()
        else:
            version_id = self.get_public_version()

        if version_id is None:
            return
        f.write('<silva_document id="%s">' % self.id)
        version = getattr(self, version_id)
        version.to_xml(context)
        f.write('</silva_document>')

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'editor_storage')
    def editor_storage(self, string=None, editor='kupu', encoding=None):
        """provide xml/xhtml/html (GET requests) and (heuristic)
           back-transforming to xml/xhtml/html (POST requests)
        """
        transformer = EditorTransformer(editor=editor)

        # we need to know what browser we are dealing with in order to know
        # what html to produce, unfortunately Mozilla uses different tags in
        # some cases (b instead of strong, i instead of em)
        browser = 'Mozilla'
        if self.REQUEST['HTTP_USER_AGENT'].find('MSIE') > -1:
            browser = 'IE'

        if string is None:
            ctx = Context(f=StringIO(),
                            last_version=1,
                            url=self.absolute_url(),
                            browser=browser,
                            model=self)
            self.to_xml(ctx)
            htmlnode = transformer.to_target(sourceobj=ctx.f.getvalue(), context=ctx)
            if encoding is not None:
                ret = htmlnode.asBytes(encoding=encoding)
                ret = ret.replace('\xa0', '&nbsp;')
            else:
                ret = unicode(htmlnode.asBytes('utf8'),'utf8')
                ret = ret.replace(u'\xa0', u'&nbsp;')
            #print 'returning:', repr(ret)
            return ret
        else:
            #print 'incoming', repr(string)
            version = self.get_editable()
            if version is None:
                raise "Hey, no version to store to!"

            ctx = Context(url=self.absolute_url(),
                            browser=browser,
                            model=self,
                            request=self.REQUEST)
            silvanode = transformer.to_source(targetobj=string, context=ctx)[0]
            title = silvanode.find('title')[0].extract_text()
            docnode = silvanode.find('doc')[0]
            content = docnode.asBytes(encoding="UTF8")
            version.content.manage_edit(content) # needs utf8-encoded string
            version.set_title(title) # needs unicode
            version.sec_update_last_author_info()

            # Clear widget cache for this version.
            version.clearEditorCache()
            #print 'storing:', repr(content)

    security.declarePrivate('get_indexables')
    def get_indexables(self):
        version = self.get_viewable()
        if version is None:
            return []
        return [version]

    def revert_to_previous(self):
        """ Create a new version of public version, throw away the
        current one.

        Overrides Versioning.revert_to_previous() to be able to clear
        the widget cache too.
        """
        Document.inheritedAttribute('revert_to_previous')(self)
        version = self.get_editable()
        version.clearEditorCache()

    def manage_beforeDelete(self, item, container):
        Document.inheritedAttribute('manage_beforeDelete')(self, item, container)
        # Does the widget cache needs be cleared for all versions - I think so...
        for version in self._get_indexable_versions():
            version_object = getattr(self, str(version), None)
            if version_object:
                self.service_editor.clearCache(version_object.content)

    security.declarePublic('PUT')
    def PUT(self, REQUEST):
        """PUT support"""
        try:
            html = REQUEST['BODYFILE'].read()
            self.editor_storage(html, 'kupu')

            # invalidate Document cache
            version = self.get_editable()
            version.clearEditorCache()

            # XXX This can be removed, right?
            transformed = self.editor_storage(editor='kupu', encoding="UTF-8")

            return transformed
        except:
            # a tad ugly, but for debug purposes it would be nice to see
            # what's actually gone wrong
            import sys, traceback
            exc, e, tb = sys.exc_info()
            print '%s: %s' % (exc, e)
            print '\n%s' % '\n'.join(traceback.format_tb(tb))
            print
            # reraise the exception so the enduser at least sees something's
            # gone wrong
            raise

InitializeClass(Document)

class DocumentVersion(CatalogedVersion):
    """Silva Document version.
    """
    meta_type = "Silva Document Version"
    __implements__ = IVersion

    security = ClassSecurityInfo()

    manage_options = (
        {'label':'Edit',       'action':'manage_main'},
        ) + CatalogedVersion.manage_options

    def __init__(self, id, title):
        DocumentVersion.inheritedAttribute('__init__')(self, id, title)
        self.content = ParsedXML('content', '<doc></doc>')

    # display edit screen as main management screen
    security.declareProtected('View management screens', 'manage_main')
    manage_main = PageTemplateFile('www/documentVersionEdit', globals())

    def to_xml(self, context):
        f = context.f
        f.write('<title>%s</title>' % translateCdata(self.get_title()))
        self.content.documentElement.writeStream(f)
        export_metadata(self, context)

    def manage_afterClone(self, item):
        # if we're a copy, clear cache
        # XXX should be part of workflow system
        self.clearEditorCache()

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'fulltext')
    def fulltext(self):
        """Return the content of this object without any xml"""
        if self.version_status() == 'unapproved':
            return ''
        return [self.get_title(), self._flattenxml(self.content_xml())]

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'content_xml')
    def content_xml(self):
        """Returns the documentElement of the content's XML
        """
        s = StringIO()
        self.content.documentElement.writeStream(s)
        value = s.getvalue()
        s.close()
        return value

    def _flattenxml(self, xmlinput):
        """Cuts out all the XML-tags, helper for fulltext (for content-objects)
        """
        # XXX this need to be fixed by using ZCTextIndex or the like
        return xmlinput

    def clearEditorCache(self):
        """ Clears editor cache for this version
        """
        editor_service = self.service_editor
        document_element = self.content.documentElement
        editor_service.clearCache(document_element)

InitializeClass(DocumentVersion)

manage_addDocumentForm = PageTemplateFile("www/documentAdd", globals(),
                                          __name__='manage_addDocumentForm')

def manage_addDocument(self, id, title, REQUEST=None):
    """Add a Document."""
    if not mangle.Id(self, id).isValid():
        return
    object = Document(id)
    self._setObject(id, object)
    object = getattr(self, id)
    object.manage_addProduct['SilvaDocument'].manage_addDocumentVersion(
        '0', title)
    object.create_version('0', None, None)
    add_and_edit(self, id, REQUEST)
    return ''

manage_addDocumentVersionForm = PageTemplateFile(
    "www/documentVersionAdd",
    globals(),
    __name__='manage_addDocumentVersionForm')

def manage_addDocumentVersion(self, id, title, REQUEST=None):
    """Add a Document version to the Silva-instance."""
    version = DocumentVersion(id, title)
    self._setObject(id, version)

    version = self._getOb(id)
    version.set_title(title)

    add_and_edit(self, id, REQUEST)
    return ''

def xml_import_handler(object, node):
    id = get_xml_id(node)
    title = get_xml_title(node)

    id = str(mangle.Id(object, id).unique())
    object.manage_addProduct['SilvaDocument'].manage_addDocument(id, title)

    newdoc = getattr(object, id)
    newdoc.sec_update_last_author_info()

    for child in node.childNodes:
        if child.nodeName == u'doc':
            version = getattr(newdoc, '0')
            childxml = writeStream(child).getvalue().encode('utf8')
            version.content.manage_edit(childxml) # expects utf8
        elif hasattr(newdoc, 'set_%s' % child.nodeName.encode('utf8')) \
                and child.nodeValue:
            getattr(newdoc, 'set_%s' % child.nodeName.encode('utf8'))(
                child.nodeValue.encode('utf8'))

    return newdoc

class SilvaDocumentPolicy(Persistent):

    __implements__ = IContainerPolicy

    def createDefaultDocument(self, container, title):
        container.manage_addProduct['SilvaDocument'].manage_addDocument(
            'index', title)
        container.index.sec_update_last_author_info()

