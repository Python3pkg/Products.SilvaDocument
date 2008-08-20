# Copyright (c) 2002-2007 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

"""Install for Silva Document
"""
from zope import interface

from Products.Silva.install import add_fss_directory_view
from Products.Silva.interfaces import IInvisibleService
from Products.SilvaDocument import Document
import EditorSupportNested

from Products.SilvaDocument import externalsource

_ = lambda x: x

def configureMiscServices(root):
    # add editor support service
    EditorSupportNested.manage_addEditorSupport(root)

def install(root):
    # create the core views from filesystem
    add_fss_directory_view(root.service_views,
                           'SilvaDocument', __file__, 'views')
    # also register views
    registerViews(root.service_view_registry)

    # configure XML widgets
    configureXMLWidgets(root)
    # security
    root.manage_permission('Add Silva Documents',
                           ['Author', 'Editor', 'ChiefEditor', 'Manager'])
    root.manage_permission('Add Silva Document Versions',
                           ['Author', 'Editor', 'ChiefEditor', 'Manager'])

    # set up/refresh some mandatory services
    configureMiscServices(root)
    
    root.service_metadata.addTypesMapping(
        ('Silva Document Version', ), ('silva-content', 'silva-extra'))
    root.service_metadata.initializeMetadata()

    root.service_containerpolicy.register(
        'Silva Document', Document.SilvaDocumentPolicy, -1)

    if hasattr(root, 'service_codesource_charset'):
        root.manage_renameObject(
            'service_codesource_charset', 'service_old_codesource_charset')
    elif not hasattr(root, 'service_old_codesource_charset'):
        root.manage_addProduct[
            'SilvaDocument'].manage_addCodeSourceCharsetService(
            'service_old_codesource_charset', 'Service Charset for Codesources')
        
def uninstall(root):
    unregisterViews(root.service_view_registry)
    unconfigureXMLWidgets(root)
    root.service_views.manage_delObjects(['SilvaDocument'])
    root.manage_delObjects(['service_editorsupport'])
    # uninstall metadata mapping?
    root.service_containerpolicy.unregister('Silva Document')
    if hasattr(root, 'service_old_codesource_charset'):
        root.manage_delObjects(['service_old_codesource_charset'])
    
def is_installed(root):
    return hasattr(root.service_views, 'SilvaDocument')

def registerViews(reg):
    """Register core views on registry.
    """
    # edit
    reg.register('edit', 'Silva Document', ['edit', 'VersionedContent', 'Document'])
    
def unregisterViews(reg):
    """Unregister core views.
    """
    reg.unregister('edit', 'Silva Document')

def configureXMLWidgets(root):
    """Configure XMLWidgets registries, editor, etc'
    """
    # create the core widgets from the filesystem
    add_fss_directory_view(root, 'service_widgets', __file__, 'widgets')

    # create the editor service
    root.manage_addProduct['XMLWidgets'].manage_addEditorService(
        'service_editor')
    # create the services for XMLWidgets
    for name in ['service_doc_editor', 
                 'service_doc_viewer',
                 'service_field_editor', 'service_field_viewer',
                 'service_nlist_editor', 'service_nlist_previewer',
                 'service_nlist_viewer',
                 'service_sub_editor', 'service_sub_previewer',
                 'service_sub_viewer',
                 'service_table_editor', 'service_table_viewer']:
        root.manage_addProduct['XMLWidgets'].manage_addWidgetRegistry(name)
        interface.alsoProvides(root[name], IInvisibleService)

    # now register all widgets
    # XXX not really necessary; the "install" should take case of this
    registerCoreWidgets(root)
    
def unconfigureXMLWidgets(root):
    root.manage_delObjects(['service_widgets', 'service_editor'])
    root.manage_delObjects([
        'service_doc_editor', 
        'service_doc_viewer',
        'service_field_editor', 'service_field_viewer',
        'service_nlist_editor', 'service_nlist_previewer',
        'service_nlist_viewer',
        'service_sub_editor', 'service_sub_previewer',
        'service_sub_viewer',
        'service_table_editor', 'service_table_viewer'])
    
def registerCoreWidgets(root):
    """ register the core widgets at the corresponding registries.
    this function assumes the registries already exist.
    """
    registerDocEditor(root)
    registerDocViewer(root)
    registerFieldEditor(root)
    registerFieldViewer(root)
    registerNListEditor(root)
    registerNListPreviewer(root)
    registerNListViewer(root)
    registerSubEditor(root)
    registerSubPreviewer(root)
    registerSubViewer(root)
    registerTableEditor(root)
    registerTableViewer(root)

def registerDocEditor(root):
    wr = root.service_doc_editor
    wr.clearWidgets()

    wr.addWidget('doc', ('service_widgets', 'top', 'doc', 'mode_normal'))

    for nodeName in ['p', 'heading', 'list', 'pre', 'toc', 'image', 'table',
                     'nlist', 'dlist', 'code', 'cite']:
        wr.addWidget(nodeName,
                     ('service_widgets', 'element', 'doc_elements',
                           nodeName, 'mode_normal'))

    wr.setDisplayName('doc', unicode(_('title')))
    wr.setDisplayName('p', unicode(_('paragraph')))
    wr.setDisplayName('heading', _('heading'))
    wr.setDisplayName('list', _('list'))
    wr.setDisplayName('pre', _('preformatted'))
    wr.setDisplayName('toc', _('table of contents'))
    wr.setDisplayName('image', _('image'))
    wr.setDisplayName('table', _('table'))
    wr.setDisplayName('nlist', _('complex list'))
    wr.setDisplayName('dlist', _('definition list'))
    wr.setDisplayName('code', _('code element'))
    wr.setDisplayName('cite', _('citation'))

    wr.setAllowed('doc', [
        'p', 'heading', 'list', 'dlist', 'pre', 'cite', 'image', 
        'table', 'nlist', 'toc'])

    if externalsource.AVAILABLE:
        wr.addWidget('source', (
            'service_widgets', 'element', 'doc_elements', 'source', 'mode_normal'))
        wr.setDisplayName('source', _('external source'))
        allowed = wr.getAllowed('doc')
        allowed.append('source')
        wr.setAllowed('doc', allowed)

def registerDocViewer(root):
    wr = root.service_doc_viewer
    wr.clearWidgets()

    wr.addWidget('doc', ('service_widgets', 'top', 'doc', 'mode_view'))

    for name in ['p', 'list', 'heading', 'pre', 'toc', 'image', 'nlist',
                 'table', 'dlist', 'code', 'cite']:
        wr.addWidget(name, ('service_widgets', 'element', 'doc_elements',
                                 name, 'mode_view'))
     
    if externalsource.AVAILABLE:
        wr.addWidget('source', (
            'service_widgets', 'element', 'doc_elements', 'source', 'mode_view'))


def registerFieldEditor(root):
    wr = root.service_field_editor
    wr.clearWidgets()

    wr.addWidget('doc', ('service_widgets', 'top', 'field', 'mode_normal'))

    for nodeName in ['p', 'heading', 'list', 'image', 'nlist']:
        wr.addWidget(nodeName,
                     ('service_widgets', 'element', 'doc_elements',
                           nodeName, 'mode_normal'))

    wr.setDisplayName('p', _('Paragraph'))
    wr.setDisplayName('heading', _('Heading'))
    wr.setDisplayName('list', _('List'))
    wr.setDisplayName('image', _('Image'))
    wr.setDisplayName('nlist', _('Complex list'))

    wr.setAllowed('doc', ['p', 'heading', 'list', 'nlist', 'image'])

def registerFieldViewer(root):
    wr = root.service_field_viewer
    wr.clearWidgets()

    wr.addWidget('doc', ('service_widgets', 'top', 'field', 'mode_view'))

    for name in ['p', 'list', 'heading', 'image', 'nlist']:
        wr.addWidget(name, ('service_widgets', 'element', 'doc_elements',
                                  name, 'mode_view'))

def registerNListEditor(root):
    wr = root.service_nlist_editor
    wr.clearWidgets()

    wr.addWidget('nlist', ('service_widgets', 'top', 'nlist', 'mode_normal'))
    
    for nodeName in ['li']:
        wr.addWidget(nodeName, 
                     ('service_widgets', 'element', 'nlist_elements',
                           nodeName, 'mode_normal'))
        
    wr.setDisplayName('nlist', _('Complex list'))
    wr.setDisplayName('li', _('List item'))
    wr.setDisplayName('title', _('List title'))
    
    wr.setAllowed('nlist', ['li'])
    
def registerNListPreviewer(root):
    wr = root.service_nlist_previewer
    wr.clearWidgets()

    wr.addWidget('nlist', ('service_widgets', 'top', 'nlist', 'mode_view'))
    
    for name in ['li']:
        wr.addWidget(name, ('service_widgets', 'element', 'nlist_elements',
                                name, 'mode_view'))

def registerNListViewer(root):
    wr = root.service_nlist_viewer
    wr.clearWidgets()
    
    wr.addWidget('nlist', ('service_widgets', 'top', 'nlist', 'mode_view'))
    
    for name in ['li']:
        wr.addWidget(name, ('service_widgets', 'element', 'nlist_elements',
                                 name, 'mode_view'))

def registerSubEditor(root):
    wr = root.service_sub_editor
    wr.clearWidgets()

    wr.addWidget('doc', ('service_widgets', 'top', 'sub', 'mode_normal'))
    wr.addWidget('li', ('service_widgets', 'top', 'sub', 'mode_normal'))
    wr.addWidget('field', ('service_widgets', 'top', 'sub', 'mode_normal'))
    
    for nodeName in ['p', 'heading', 'list', 'image', 'nlist', 'pre', 'dlist']:
        wr.addWidget(nodeName, 
                     ('service_widgets', 'element', 'doc_elements',
                           nodeName, 'mode_normal'))
        
    wr.setDisplayName('p', _('Paragraph'))
    wr.setDisplayName('heading', _('Heading'))
    wr.setDisplayName('list', _('List'))
    wr.setDisplayName('image', _('Image'))
    wr.setDisplayName('nlist', _('Complex list'))
    wr.setDisplayName('pre', _('Preformatted'))
    wr.setDisplayName('dlist', _('Definition list'))

    for nodeName in ('doc', 'li', 'field'):
        wr.setAllowed(nodeName,  ['p', 'heading', 'list', 'nlist', 'image',
                                     'pre', 'dlist'])

def registerSubPreviewer(root):
    wr = root.service_sub_previewer
    wr.clearWidgets()
    
    wr.addWidget('doc', ('service_widgets', 'top', 'sub', 'mode_view'))
    wr.addWidget('li', ('service_widgets', 'top', 'sub', 'mode_view'))
    wr.addWidget('field', ('service_widgets', 'top', 'sub', 'mode_view'))
    
    for name in ['p', 'list', 'heading', 'nlist', 'pre', 'dlist']:
        wr.addWidget(name, ('service_widgets', 'element', 'doc_elements',
                                 name, 'mode_view'))
        
    # XX originally used mode_preview here, why?
    #wr.addWidget('image', ('service_widgets', 'element', 'doc_elements',
    #                           'image', 'mode_preview'))
    wr.addWidget('image', ('service_widgets', 'element', 'doc_elements',
                                'image', 'mode_view'))

def registerSubViewer(root):
    wr = root.service_sub_viewer
    wr.clearWidgets()
    
    wr.addWidget('doc', ('service_widgets', 'top', 'sub', 'mode_view'))
    wr.addWidget('li', ('service_widgets', 'top', 'sub', 'mode_view'))
    wr.addWidget('field', ('service_widgets', 'top', 'sub', 'mode_view'))
    
    for name in ['p', 'list', 'heading', 'image', 'nlist', 'pre', 'dlist']:
        wr.addWidget(name, ('service_widgets', 'element', 'doc_elements',
                                 name, 'mode_view'))

def registerTableEditor(root):
    wr = root.service_table_editor
    wr.clearWidgets()
    
    wr.addWidget('table', ('service_widgets', 'top', 'table', 'mode_normal'))
    
    for nodeName in ['row', 'row_heading']:
        wr.addWidget(nodeName, 
                     ('service_widgets', 'element', 'table_elements',
                           nodeName, 'mode_normal'))

    # add a field that doesn't do any displaying, just for sub editor invocation
    wr.addWidget('field',
                 ('service_widgets', 'element', 'table_elements', 'field'))
    wr.setDisplayName('table', _('Table'))
    wr.setDisplayName('row', _('row'))
    wr.setDisplayName('row_heading', _('row heading'))
    
    wr.setAllowed('table', ['row', 'row_heading'])

def registerTableViewer(root):
    wr = root.service_table_viewer
    wr.clearWidgets()
    
    wr.addWidget('table', ('service_widgets', 'top', 'table', 'mode_view'))
    
    for name in ['row', 'row_heading']:
        wr.addWidget(name, ('service_widgets', 'element', 'table_elements',
                                 name, 'mode_view'))

