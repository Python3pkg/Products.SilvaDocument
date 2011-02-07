# Copyright (c) 2002-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from silva.core.interfaces import IVersionedContent, IVersion


class IDocument(IVersionedContent):
    """A document let you store and edit rich text using different editors.
    """


class IDocumentVersion(IVersion):
    """This is a version of a document.
    """

    def get_document_xml():
        """Return the document XML of the document.
        """

    def get_document_xml_as(format='kupu', request=None):
        """Return the XML of the document converted in a different
        format. By default it will be HTML that can be edited by Kupu.
        """

    def set_document_xml_from(data, format='kupu', request=None):
        """This change the document XML to data. Data is converted to
        the document XML from the input format, which is Kupu by
        default.
        """
