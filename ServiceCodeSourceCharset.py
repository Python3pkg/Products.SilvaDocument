import Globals
from OFS.SimpleItem import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo

from Products.Silva.helpers import add_and_edit
from Products.Silva.i18n import translate as _

manage_permission = 'Manage CodeSource Charset Services'

class CodeSourceCharsetService(SimpleItem):
    
    security = ClassSecurityInfo()
    meta_type = 'Silva CodeSource Charset Service'

    manage_options = ({'label': 'Edit', 'action': 'edit_tab'},
                        ) + SimpleItem.manage_options

    security.declareProtected(manage_permission, 'edit_tab')
    security.declareProtected(manage_permission, 'manage_main')
    manage_main = edit_tab = PageTemplateFile('www/serviceCodeSourceCharsetEditTab',
                                                globals(), __name__='edit_tab')

    def __init__(self, id, title):
        self.id = id
        self.title = title
        self._charset = 'cp1252'

    security.declarePublic('charset')
    def charset(self):
        """Return the charset"""
        return self._charset

    security.declareProtected(manage_permission, 'set_charset')
    def set_charset(self, charset):
        """Set the charset"""
        self._charset = charset

    security.declareProtected(manage_permission, 'manage_setCharset')
    def manage_setCharset(self, REQUEST):
        """Manage method to set the charset"""
        if not REQUEST.has_key('charset'):
            return self.edit_tab(manage_tabs_message=_('No charset entered'))
        self.set_charset(REQUEST['charset'])
        return self.edit_tab(manage_tabs_message=_('Charset set'))

Globals.InitializeClass(CodeSourceCharsetService)

manage_addCodeSourceCharsetServiceForm = PageTemplateFile(
        'www/serviceCodeSourceCharsetAdd', globals(),
        __name__ = 'manage_addCodeSourceCharsetServiceForm')

def manage_addCodeSourceCharsetService(self, id, title, REQUEST=None):
    """Add a service"""
    id = self._setObject(id, CodeSourceCharsetService(id, title))
    add_and_edit(self, id, REQUEST)
    return ''
