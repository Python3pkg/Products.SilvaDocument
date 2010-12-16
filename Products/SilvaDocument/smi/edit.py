# -*- coding: utf-8 -*-
# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from zope.interface import alsoProvides
from silva.core.smi import smi as silvasmi
from silva.core.smi import interfaces
from silva.core.layout.jquery.interfaces import IJQueryResources
from Products.SilvaDocument.interfaces import IDocument
from silva.core import conf as silvaconf
from infrae import rest
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
        self.document = None
        version = self.context.get_editable()
        if version is not None:
            self.document = version.get_document_xml_as(request=self.request)
        # If self.document is None


class RESTSaveDocument(rest.REST):
    """Save document.
    """
    grok.context(IDocument)
    grok.name('silva.document.save')

    format = 'ckeditor'

    def POST(self, content):
        version = self.context.get_editable()
        if version is None:
            raise BadRequest('Document is not editable')
        version.set_document_xml_from(
            u"<body>" + unicode(content, 'utf-8') + u"</body>",
            request=self.request, format=self.format)
        return version.get_document_xml_as(
            request=self.request, format=self.format)

