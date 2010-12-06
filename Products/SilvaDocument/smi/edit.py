from five import grok
from zope.interface import alsoProvides
from silva.core.smi import smi as silvasmi
from silva.core.smi import interfaces
from silva.core.layout.jquery.interfaces import IJQueryResources
from Products.SilvaDocument.interfaces import IDocument
from silva.core import conf as silvaconf
import zeam.form.silva as silvaforms
from zExceptions import BadRequest

grok.layer(interfaces.ISMILayer)


class ICKEditorResources(IJQueryResources):
    """ Resource for CKEditor
    """
    silvaconf.resource('ckeditor/ckeditor.js')
    silvaconf.resource('ckeditor/adapters/jquery.js')
    silvaconf.resource('editor.js')


class SMITabEdit(silvasmi.SMIPage):
    """CKEditor edit page for silva document.
    """
    grok.context(IDocument)
    grok.implements(interfaces.IEditTab,
                    interfaces.ISMITabIndex,
                    interfaces.ISMINavigationOff)
    grok.name('tab_edit_cke')

    tab = 'edit'

    def update(self):
        alsoProvides(self.request, ICKEditorResources)
        self.document = self.context.get_editable().get_document_xml_as(
            request=self.request)


class EditorSaveDocument(silvasmi.SilvaForm):
    """ A form to save the document
    """
    grok.context(IDocument)
    grok.name('editor_save')

    fields = silvaforms.Fields(
        silvaforms.Field('content', required=True))
    ignoreContent = True
    ignoreRequest = False
    tab = 'edit'

    @silvaforms.action('save', method="post")
    def save(self):
        data, errors = self.extractData()
        if errors:
            raise BadRequest(errors)
        version = self.context.get_editable()
        if version is None:
            raise BadRequest('invalid version')
        version.set_document_xml_from(data['content'])
        return silvaforms.SUCCESS

    def render(self):
        return u''

