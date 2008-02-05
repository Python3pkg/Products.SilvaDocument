# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: interfaces.py,v 1.9 2006/01/24 16:15:05 faassen Exp $

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
    pass

class IDocumentVersion(IVersion):
    pass
