from five import grok
from zope.interface import alsoProvides
from silva.core.smi import smi as silvasmi
from silva.core.smi import interfaces
from silva.core.layout.jquery.interfaces import IJQueryResources
from Products.SilvaDocument.interfaces import IDocument
from silva.core import conf as silvaconf

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
    grok.name('tab_edit')

    tab = 'edit'

    def update(self):
        alsoProvides(self.request, ICKEditorResources)
        self.document = self.context.get_editable().get_document_xml_as(
            request=self.request)


