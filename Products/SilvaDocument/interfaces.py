# -*- coding: utf-8 -*-
# Copyright (c) 2002-2012 Infrae. All rights reserved.
# See also LICENSE.txt

from silva.core.interfaces import IVersionedContent, IVersion
from zope import interface


class IPath(interface.Interface):

    def pathToUrl(path):
        """Convert a physical path to a URL.
        """

    def urlToPath(url):
        """Convert a HTTP URL to a physical path.
        """


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
