# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Python
from __future__ import nested_scopes

# Zope
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from zope import interface

# Silva
from Products.Silva import SilvaPermissions
from Products.Silva.BaseService import SilvaService
from silva.core.interfaces import IInvisibleService

# SilvaDocument
from Products.SilvaDocument import externalsource    
from Products.SilvaDocument import mixedcontentsupport

from silva.core import conf as silvaconf

mixedContentSupportRegistry = mixedcontentsupport.SupportRegistry(
    mixedcontentsupport.ParagraphSupport)

mixedContentSupportRegistry.registerElementDefault(
    'heading', mixedcontentsupport.HeadingSupport)
    
mixedContentSupportRegistry.registerElementDefault(
    'pre', mixedcontentsupport.PreSupport)    
    
class EditorSupport(SilvaService):
    """XML editor support.
    """
    
    security = ClassSecurityInfo()
    interface.implements(IInvisibleService)
    meta_type = 'Silva Editor Support Service'

    silvaconf.icon('www/editorservice.gif')
    silvaconf.factory('manage_addEditorSupport')

    def __init__(self, id):
        self.id = id

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'getMixedContentSupport')
    def getMixedContentSupport(self, context, node):
        supportklass = mixedContentSupportRegistry.lookup(context, node)
        return supportklass(node).__of__(context)
        
    # Make the external source integration code available through the
    # service_editorsupport in Silva.
    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'availableSources')
    def availableSources(self, context):
        return externalsource.availableSources(context)

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'getSourceForId')
    def getSourceForId(self, context, id):
        return externalsource.getSourceForId(context, id)
    
    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'getSourceParameters')
    def getSourceParameters(self, context, node):
        return externalsource.getSourceParameters(context, node)
    
    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'isSourceCacheable')
    def isSourceCacheable(self, context, node):
        return externalsource.isSourceCacheable(context, node)
    
    security.declarePublic('replace_xml_entities')
    def replace_xml_entities(self, text):
        """Replace all disallowed characters with XML-entities"""
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        text = text.replace('"', '&quot;')
        return text
    
    # XXX Original methods left here for backwards compatiblity - other
    # Silva extensions might still be using these... Please use the 
    # getMixedContentSupport() method instead!
    
    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'render_text_as_html')
    def render_text_as_html(self, node, show_index=0):
        supp = mixedContentSupportRegistry.lookupByName(
            None, node.nodeName)
        return supp(node).renderHTML()
    
    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'render_heading_as_html')
    def render_heading_as_html(self, node, show_index=0):
        supp = mixedContentSupportRegistry.lookupByName(
            None, node.nodeName)
        return supp(node).renderHTML()
    
    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'render_text_as_editable')
    def render_text_as_editable(self, node):
        supp = mixedContentSupportRegistry.lookupByName(
            None, node.nodeName)
        return supp(node).renderEditable()

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'render_heading_as_editable')
    def render_heading_as_editable(self, node):
        supp = mixedContentSupportRegistry.lookupByName(
            None, node.nodeName)
        return supp(node).renderEditable()

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'render_pre_as_editable')
    def render_pre_as_editable(self, node):
        supp = mixedContentSupportRegistry.lookupByName(
            None, node.nodeName)
        return supp(node).renderEditable()

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'replace_text')
    def replace_text(self, node, st, parser=None):
        supp = mixedContentSupportRegistry.lookupByName(
            None, node.nodeName)
        return supp(node).parse(st)
    
    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'replace_pre')
    def replace_pre(self, node, st):
        supp = mixedContentSupportRegistry.lookupByName(
            None, node.nodeName)
        return supp(node).parse(st)
    
    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'replace_heading')
    def replace_heading(self, node, st):
        supp = mixedContentSupportRegistry.lookupByName(
            None, node.nodeName)
        return supp(node).parse(st)
    
InitializeClass(EditorSupport)

def manage_addEditorSupport(container):
    "editor support service factory"
    id = 'service_editorsupport'
    container._setObject(id, EditorSupport(id))
