# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: __init__.py,v 1.6 2003/09/29 08:20:35 zagy Exp $

from Products.Silva.ExtensionRegistry import extensionRegistry
from Products.Silva.ImporterRegistry import importer_registry
import EditorSupportNested
import install

from Products.Silva.fssite import registerDirectory
from Products.SilvaMetadata.Compatibility import registerTypeForMetadata

from Products.SilvaDocument import Document

def initialize(context):
    extensionRegistry.register(
        'SilvaDocument', 'Silva Document', context, [Document],
        install, depends_on='Silva')
    
    context.registerClass(
        EditorSupportNested.EditorSupport,
        constructors = (EditorSupportNested.manage_addEditorSupport, ),
        icon = "www/editorservice.gif"
        )
    
    importer_registry.register_tag('silva_document',
                                   Document.xml_import_handler)
    registerDirectory('views', globals())
    registerDirectory('widgets', globals())
    
    registerTypeForMetadata(Document.DocumentVersion.meta_type)

    initialize_upgrade()


def initialize_upgrade():
    from Products.SilvaDocument import upgrade
    upgrade.initialize()

