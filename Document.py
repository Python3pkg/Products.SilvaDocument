# Copyright (c) 2002-2007 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Python
from StringIO import StringIO
import re
import sys
import traceback

# Zope
from zope.interface import implements
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Globals import InitializeClass
from Persistence import Persistent
from zExceptions import InternalError

from Products.ParsedXML.ParsedXML import ParsedXML

# Silva
from Products.Silva import SilvaPermissions
from Products.Silva.VersionedContent import CatalogedVersionedContent
from Products.Silva.Version import CatalogedVersion
from Products.Silva import mangle
from Products.Silva.ContentObjectFactoryRegistry import contentObjectFactoryRegistry

# For XML-Conversions for editors
from transform.Transformer import EditorTransformer
from transform.base import Context

from Products.Silva.interfaces import IContainerPolicy
from Products.SilvaDocument.interfaces import IDocument, IDocumentVersion
from Products.SilvaDocument.i18n import translate as _

from Products.SilvaDocument import externalsource

from Products.SilvaMetadata.Exceptions import BindingError

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

    implements(IDocument)

    # some scary DAV stuff...
    __dav_collection__ = False
    isAnObjectManager = False

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
        non_cacheable_elements = ['toc', 'code',]

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
                raise _("No version to store to!")

            # get any metadata elements saved to the metadata
            # XXX currently uses a completely different machinery to parse
            # the XML, perhaps we want to move that to the transformations
            # at some point (but would require too much hacking for now)
            errors = self._set_metadata_from_html(string, version)
            if errors:
                raise BindingError, errors

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

    def _set_metadata_from_html(self, html, version):
        """Rip the metadata out of the HTML (meta tags), set it on version"""
        # XXX obviously it would make sense if the transformations could 
        # tackle this instead of doing it seperately, however, they are messy
        # enough as they are now (and not capable of such a thing yet)
        
        # XXX SAX took about 2 seconds (!) to get the meta values,
        # so I decided to try re instead... this made sense, parsing now takes
        # less than one hundreth of a second (usually even less than one 
        # thousandth!)
        metamapping = {}
        import re
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
                    found[match.group(1)] = self._deentitize(match.group(2))
                if (found.has_key('name') and found.has_key('content') and 
                        found.has_key('scheme')):
                    if not metamapping.has_key(found['scheme']):
                        metamapping[found['scheme']] = {}
                    metamapping[found['scheme']][found['name']] = found['content']

        errors = {}
        binding = self.service_metadata.getMetadata(self.get_editable())
        for namespace, values in metamapping.items():
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
    
    def _deentitize(self, xml):
        return xml.replace('&lt;', '<').replace('&gt;', '>').\
                replace('&quot;', '"').replace('&amp;', '&')

    def revert_to_previous(self):
        """ Create a new version of public version, throw away the
        current one.

        Overrides Versioning.revert_to_previous() to be able to clear
        the widget cache too.
        """
        Document.inheritedAttribute('revert_to_previous')(self)
        version = self.get_editable()
        version.clearEditorCache()

    def transform_and_store(self, content_type, content):
        ret = content
        try:
            if content_type.split(';')[0] in ['text/html', 'application/xhtml+xml']:
                html = content
                self.editor_storage(html, 'kupu')

                # invalidate Document cache
                version = self.get_editable()
                version.clearEditorCache()

                # XXX This can be removed, right?
                ret = self.editor_storage(editor='kupu', encoding="UTF-8")
            else:
                # plain Silva document XML
                self.get_editable().content.manage_edit(content)
        except:
            # a tad ugly, but for debug purposes it would be nice to see
            # what's actually gone wrong
            exc, e, tb = sys.exc_info()
            # XXX should store to zLog instead
            print '%s: %s' % (exc, e)
            print '\n%s' % '\n'.join(traceback.format_tb(tb))
            print
            # reraise the exception so the enduser at least sees something's
            # gone wrong
            raise
        return ret

    # WebDAV API
    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                                'PUT')
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
            raise InternalError, 'no editable version available'
        content = REQUEST['BODYFILE'].read()
        content_type = self._get_content_type_from_request(REQUEST, content)
        ret = self.transform_and_store(content_type, content)

    def _get_content_type_from_request(self, request, content):
        """tries to figure out the content type of a PUT body from a request

            the request may not have a content-type header available, if so
            we should use the contents itself to determine the content type
        """
        ct = request.get_header('content-type')
        if ct is not None:
            return ct
        content = re.sub('<?.*?>', '', content).strip()
        if content.startswith('<html') or content.startswith('<!DOCTYPE html'):
            return 'text/html'
        return 'application/x-silva-document-xml'

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                                'manage_FTPget')
    def manage_FTPget(self):
        """return the raw XML-contents of this document"""
        editable = self.get_previewable()
        if editable is None:
            raise InternalError, 'no viewable version available'
        f = StringIO()
        editable.get_xml_content(f)
        return f.getvalue()

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                                'manage_DAVget')
    manage_DAVget = manage_FTPget

InitializeClass(Document)

def document_will_be_removed(document, event):
    # Does the widget cache needs be cleared for all versions - I think so...
    for version in document._get_indexable_versions():
        version_object = getattr(document, str(version), None)
        if version_object:
            document.service_editor.clearCache(version_object.content)

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
        DocumentVersion.inheritedAttribute('__init__')(self, id)
        self.content = ParsedXML('content', '<doc></doc>')

    # display edit screen as main management screen
    security.declareProtected('View management screens', 'manage_main')
    manage_main = PageTemplateFile('www/documentVersionEdit', globals())

    def get_xml_content(self, f):
        self.content.documentElement.writeStream(f)

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'fulltext')
    def fulltext(self):
        """Return the content of this object without any xml"""
        if self.version_status() == 'unapproved':
            return ''
        return [
            self.object().id,
            self.get_title(),
            self._flattenxml(self.content_xml())]

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
        """Cuts out all the XML-tags, helper for fulltext (for
        content-objects)
        """
        # XXX: remove code sources, since the parameters are
        # potentially sensitive data.
        matchstr = re.compile(
            r'<source id=".*?">.*?</source>', re.DOTALL|re.MULTILINE)
        xmlinput = matchstr.sub('', xmlinput)
        return re.sub('<[^>]*>(?i)(?m)', ' ', xmlinput)

    def clearEditorCache(self):
        """ Clears editor cache for this version
        """
        editor_service = self.service_editor
        document_element = self.content.documentElement
        editor_service.clearCache(document_element)

InitializeClass(DocumentVersion)

def documentversion_cloned(documentversion, event):
    # if we're a copy, clear cache
    # XXX should be part of workflow system
    documentversion.clearEditorCache()


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

