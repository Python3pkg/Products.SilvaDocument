# Copyright (c) 2002-2007 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: __init__.py,v 1.12 2006/01/24 16:15:05 faassen Exp $

import EditorSupportNested
import ServiceCodeSourceCharset
import install

from Products.Silva.fssite import registerDirectory
from Products.Silva.helpers import makeContainerFilter

def initialize(context):
    from Products.SilvaDocument.silvaxml import xmlexport, xmlimport
    
    context.registerClass(
        EditorSupportNested.EditorSupport,
        constructors = (EditorSupportNested.manage_addEditorSupport, ),
        icon = "www/editorservice.gif",
        container_filter = makeContainerFilter()
        )
    
    context.registerClass(
        ServiceCodeSourceCharset.CodeSourceCharsetService,
        constructors = (ServiceCodeSourceCharset.manage_addCodeSourceCharsetServiceForm, 
                        ServiceCodeSourceCharset.manage_addCodeSourceCharsetService),
        icon = "www/editorservice.gif",
        container_filter = makeContainerFilter()
        )

    registerDirectory('widgets', globals())

    initialize_upgrade()

    # new xml import/export
    xmlexport.initializeXMLExportRegistry()
    xmlimport.initializeXMLImportRegistry()


# allow to access i18n from TTW code

from AccessControl import allow_module
allow_module('Products.SilvaDocument.i18n')


def initialize_upgrade():
    from Products.SilvaDocument import upgrade
    upgrade.initialize()

