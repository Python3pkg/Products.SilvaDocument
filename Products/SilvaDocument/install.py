# Copyright (c) 2002-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Products.Silva.install import add_fss_directory_view
from Products.SilvaDocument import Document


def configureAddables(root):
    addables = ['Silva Document']
    new_addables = root.get_silva_addables_allowed_in_container()
    for a in addables:
        if a not in new_addables:
            new_addables.append(a)
    root.set_silva_addables_allowed_in_container(new_addables)


def install(root):
    # create the core views from filesystem
    add_fss_directory_view(root.service_views,
                           'SilvaDocument', __file__, 'views')
    # also register views
    registerViews(root.service_view_registry)
    configureAddables(root)

    # security
    root.manage_permission('Add Silva Documents',
                           ['Author', 'Editor', 'ChiefEditor', 'Manager'])
    root.manage_permission('Add Silva Document Versions',
                           ['Author', 'Editor', 'ChiefEditor', 'Manager'])

    root.service_metadata.addTypesMapping(
        ('Silva Document Version', ), ('silva-content', 'silva-extra'))
    root.service_metadata.initializeMetadata()

    root.service_containerpolicy.register(
        'Silva Document', Document.SilvaDocumentPolicy, -1)


def uninstall(root):
    unregisterViews(root.service_view_registry)
    root.service_views.manage_delObjects(['SilvaDocument'])
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


def unregisterViews(reg):
    """Unregister core views.
    """
    reg.unregister('edit', 'Silva Document')

