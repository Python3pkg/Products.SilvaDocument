# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: AutoTOC.py,v 1.1 2003/07/28 13:54:56 zagy Exp $

# Zope
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Persistence import Persistent
from OFS.SimpleItem import SimpleItem

# products
from Products.ParsedXML.ParsedXML import ParsedXML

# Silva
from Products.Silva.Content import Content
from Products.Silva import SilvaPermissions
from Products.Silva import mangle
from Products.Silva.interfaces import IContent, IContainerPolicy
from Products.Silva.helpers import add_and_edit

icon="www/silvadoc.gif"

class AutoTOC(Content, SimpleItem):
    """Automatically displays table of contents"""
    security = ClassSecurityInfo()

    meta_type = "Silva AutoTOC"

    __implements__ = IContent

    def __init__(self, id, title):
        AutoTOC.inheritedAttribute('__init__')(self, id, title)
        self.content = ParsedXML('content', '<doc><toc/></doc>')

    # ACCESSORS
    security.declareProtected(SilvaPermissions.View, 'is_cacheable')
    def is_cacheable(self):
        """Return true if this document is cacheable.
        That means the document contains no dynamic elements like
        code, datasource or toc.
        """
        return 0

    def get_version(self):
        """return version"""
        # FIXME: isssue #524 could fix having to put this here
        return self.aq_inner
    
    
InitializeClass(AutoTOC)

manage_addAutoTOCForm = PageTemplateFile("www/autoTOCAdd", globals(),
    __name__='manage_addAutoTOCForm')

def manage_addAutoTOC(self, id, title, REQUEST=None):
    """Add a autotoc."""
    if not mangle.Id(self, id).isValid():
        return
    object = AutoTOC(id, title)
    self._setObject(id, object)
    add_and_edit(self, id, REQUEST)
    return ''


class _AutoTOCPolicy(Persistent):

    __implements__ = IContainerPolicy

    def createDefaultDocument(self, container, title):
        container.manage_addProduct['SilvaDocument'].manage_addAutoTOC(
            'index', title)
        container.index.sec_update_last_author_info()
AutoTOCPolicy = _AutoTOCPolicy()


