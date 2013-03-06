# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from zope.interface import Interface, alsoProvides, noLongerProvides


class IExtension(Interface):
    pass


def configure_addables(root):
    addables = ['Obsolete Document']
    new_addables = root.get_silva_addables_allowed_in_container()
    if new_addables is not None:
        for a in addables:
            if a not in new_addables:
                new_addables.append(a)
        root.set_silva_addables_allowed_in_container(new_addables)


def install(root, extension):
    # also register views
    configure_addables(root)

    # security
    root.manage_permission(
        'Add Obsolete Documents',
        ['Author', 'Editor', 'ChiefEditor', 'Manager'])
    root.manage_permission(
        'Add Obsolete Document Versions',
        ['Author', 'Editor', 'ChiefEditor', 'Manager'])
    root.service_metadata.addTypesMapping(
        ('Obsolete Document Version', ),
        ('silva-content', 'silva-extra', 'silva-settings'))
    root.service_metadata.initializeMetadata()
    alsoProvides(root, IExtension)


def uninstall(root, extension):
    noLongerProvides(root, IExtension)


def is_installed(root, extension):
    return IExtension.providedBy(root)

