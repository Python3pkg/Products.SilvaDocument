"""Install for Silva Document
"""

from Products.Silva.install import add_fss_directory_view
from Products.SilvaDocument import Document
import EditorSupportNested

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

    # set up/refresh some mandatory services
    configureMiscServices(root)

    mapping = root.service_metadata.getTypeMapping()
    mapping.editMappings('',
                         [{'type':'Silva Document Version',
                           'chain':'silva-content, silva-extra'}])

    root.service_containerpolicy.register('Silva Document',
        Document.SilvaDocumentPolicy)
        
def uninstall(root):
    unregisterViews(root.service_view_registry)
    unconfigureXMLWidgets(root)
    root.service_views.manage_delObjects(['SilvaDocument'])
    root.manage_delObjects(['service_editorsupport'])
    # uninstall metadata mapping?
    root.service_containerpolicy.unregister('Silva Document')
    
def is_installed(root):
    return hasattr(root.service_views, 'SilvaDocument')

def registerViews(reg):
    """Register core views on registry.
    """

    # edit
    reg.register('edit', 'Silva Document',
                 ['edit', 'VersionedContent', 'Document'])
    # public
    reg.register('public', 'Silva Document', ['public', 'Document'])

    # add
    reg.register('add', 'Silva Document', ['add', 'Document'])
    
def unregisterViews(reg):
    for meta_type in ['Silva Document']:
        reg.unregister('edit', meta_type)
        reg.unregister('public', meta_type)
        reg.unregister('add', meta_type)

def configureXMLWidgets(root):
    """Configure XMLWidgets registries, editor, etc'
    """
    # create the core widgets from the filesystem
    add_fss_directory_view(root, 'service_widgets', __file__, 'widgets')

    # create the editor service
    root.manage_addProduct['XMLWidgets'].manage_addEditorService(
        'service_editor')
    # create the services for XMLWidgets
    for name in ['service_doc_editor', 'service_doc_previewer',
                 'service_doc_viewer',
                 'service_field_editor', 'service_field_viewer',
                 'service_nlist_editor', 'service_nlist_previewer',
                 'service_nlist_viewer',
                 'service_sub_editor', 'service_sub_previewer',
                 'service_sub_viewer',
                 'service_table_editor', 'service_table_viewer']:
        root.manage_addProduct['XMLWidgets'].manage_addWidgetRegistry(name)

    # now register all widgets
    # XXX not really necessary; the "install" should take case of this
    registerCoreWidgets(root)
    
def unconfigureXMLWidgets(root):
    root.manage_delObjects(['service_widgets', 'service_editor'])
    root.manage_delObjects([
        'service_doc_editor', 'service_doc_previewer',
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
    registerDocPreviewer(root)
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
                     'nlist', 'dlist', 'code', 'externaldata']:
        wr.addWidget(nodeName,
                     ('service_widgets', 'element', 'doc_elements',
                           nodeName, 'mode_normal'))

    wr.setDisplayName('doc', 'Title')
    wr.setDisplayName('p', 'Paragraph')
    wr.setDisplayName('heading', 'Heading')
    wr.setDisplayName('list', 'List')
    wr.setDisplayName('pre', 'Preformatted')
    wr.setDisplayName('toc', 'Table of contents')
    wr.setDisplayName('image', 'Image')
    wr.setDisplayName('table', 'Table')
    wr.setDisplayName('nlist', 'Complex list')
    wr.setDisplayName('dlist', 'Definition list')
    wr.setDisplayName('code', 'Code Element')
    wr.setDisplayName('externaldata', 'External Data')

    wr.setAllowed('doc', ['p', 'heading', 'list', 'dlist', 'pre', 'image', 
                  'table', 'nlist', 'toc', 'code', 'externaldata'])


def registerDocViewer(root):
    wr = root.service_doc_viewer
    wr.clearWidgets()

    wr.addWidget('doc', ('service_widgets', 'top', 'doc', 'mode_view'))

    for name in ['p', 'list', 'heading', 'pre', 'toc', 'image', 'nlist',
                 'table', 'dlist', 'code', 'externaldata']:
        wr.addWidget(name, ('service_widgets', 'element', 'doc_elements',
                                 name, 'mode_view'))

def registerDocPreviewer(root):
    wr = root.service_doc_previewer
    wr.clearWidgets()

    wr.addWidget('doc', ('service_widgets', 'top', 'doc', 'mode_view'))

    for name in ['p', 'list', 'heading', 'pre', 'nlist', 'table',
                 'dlist', 'externaldata']:
        wr.addWidget(name, ('service_widgets', 'element', 'doc_elements',
                                 name, 'mode_view'))

    wr.addWidget('toc', ('service_widgets', 'element', 'doc_elements',
                             'toc', 'mode_preview'))
    wr.addWidget('image', ('service_widgets', 'element', 'doc_elements',
                                'image', 'mode_preview'))
    wr.addWidget('code', ('service_widgets', 'element', 'doc_elements',
                               'code', 'mode_preview'))

def registerFieldEditor(root):
    wr = root.service_field_editor
    wr.clearWidgets()

    wr.addWidget('doc', ('service_widgets', 'top', 'field', 'mode_normal'))

    for nodeName in ['p', 'heading', 'list', 'image', 'nlist']:
        wr.addWidget(nodeName,
                     ('service_widgets', 'element', 'doc_elements',
                           nodeName, 'mode_normal'))

    wr.setDisplayName('p', 'Paragraph')
    wr.setDisplayName('heading', 'Heading')
    wr.setDisplayName('list', 'List')
    wr.setDisplayName('image', 'Image')
    wr.setDisplayName('nlist', 'Complex list')

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
        
    wr.setDisplayName('nlist', 'Complex list')
    wr.setDisplayName('li', 'List item')
    wr.setDisplayName('title', 'List title')
    
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
        
    wr.setDisplayName('p', 'Paragraph')
    wr.setDisplayName('heading', 'Heading')
    wr.setDisplayName('list', 'List')
    wr.setDisplayName('image', 'Image')
    wr.setDisplayName('nlist', 'Complex list')
    wr.setDisplayName('pre', 'Preformatted')
    wr.setDisplayName('dlist', 'Definition list')

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
    wr.setDisplayName('table', 'Table')
    wr.setDisplayName('row', 'Row')
    wr.setDisplayName('row_heading', 'Row heading')
    
    wr.setAllowed('table', ['row', 'row_heading'])

def registerTableViewer(root):
    wr = root.service_table_viewer
    wr.clearWidgets()
    
    wr.addWidget('table', ('service_widgets', 'top', 'table', 'mode_view'))
    
    for name in ['row', 'row_heading']:
        wr.addWidget(name, ('service_widgets', 'element', 'table_elements',
                                 name, 'mode_view'))

