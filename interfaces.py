# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.interface import Interface, Attribute
from Products.Silva.interfaces import IVersionedContent, IVersion

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
        pass
    
    def renderHTML(view_type='public'):
        """ Render the node to HTML.
        
        Specify the view_type for this render: 'public' or 'edit'.
        """
        pass
    
    def renderEditable():
        """ Render the node to user editable text.
        
        Complementary to parse().
        """
        pass

class IDocument(IVersionedContent):
    def kupu_editor_supported():
        """ returns true if the kupu editor is
            supported for this type of document.
            To support disabling the kupu smi button
            in the middleground"""
        
    def forms_editor_supported():
        """ returns true if the forms-based editor
            is supported for this type of document
            To support disabling the forms editor
            smi button in the middleground"""

class IDocumentVersion(IVersion):
    pass
