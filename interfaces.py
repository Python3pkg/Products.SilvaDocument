# Copyright (c) 2002-2005 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: interfaces.py,v 1.6 2005/01/19 14:28:50 faassen Exp $

from Interface import Interface, Attribute

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
