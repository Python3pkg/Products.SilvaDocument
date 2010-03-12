# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.interface import Interface, Attribute
from silva.core.interfaces import IVersionedContent, IVersion


class IMixedContentSupport(Interface):
    """ Support of editing and rendering mixed content XML (i.e.
    XML elements containing both text- and child nodes).
    """

    _node = Attribute("XXX something on the node attritbute here")

    def parse(input_string):
        """ Parse the user input to a DOM fragment for inclusion
        in the Document being edited.

        Complementary to render_editable().
        """

    def renderHTML(view_type='public'):
        """ Render the node to HTML.

        Specify the view_type for this render: 'public' or 'edit'.
        """

    def renderEditable():
        """ Render the node to user editable text.

        Complementary to parse().
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
