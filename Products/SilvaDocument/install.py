# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Products.SilvaDocument import Document


def configureAddables(root):
    addables = ['Silva Document']
    new_addables = root.get_silva_addables_allowed_in_container()
    for a in addables:
        if a not in new_addables:
            new_addables.append(a)
    root.set_silva_addables_allowed_in_container(new_addables)


def install(root):
    # also register views
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
    root.service_containerpolicy.unregister('Silva Document')


def is_installed(root):
    return False

