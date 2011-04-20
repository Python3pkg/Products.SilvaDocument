# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.interface import Interface, alsoProvides, noLongerProvides


class IExtension(Interface):
    pass


def configure_addables(root):
    addables = ['Silva Document']
    new_addables = root.get_silva_addables_allowed_in_container()
    if new_addables is not None:
        for a in addables:
            if a not in new_addables:
                new_addables.append(a)
        root.set_silva_addables_allowed_in_container(new_addables)


def install(root):
    # also register views
    configure_addables(root)

    # security
    root.manage_permission('Add Silva Documents',
                           ['Author', 'Editor', 'ChiefEditor', 'Manager'])
    root.manage_permission('Add Silva Document Versions',
                           ['Author', 'Editor', 'ChiefEditor', 'Manager'])
    root.service_metadata.addTypesMapping(
        ('Silva Document Version', ), ('silva-content', 'silva-extra'))
    root.service_metadata.initializeMetadata()
    alsoProvides(root, IExtension)


def uninstall(root):
    noLongerProvides(root, IExtension)


def is_installed(root):
    return IExtension.providedBy(root)

