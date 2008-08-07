# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Products.Silva.fssite import registerDirectory

from silva.core import conf as silvaconf
silvaconf.extensionName('SilvaDocument')
silvaconf.extensionTitle('Silva Document')

def initialize(context):
    from Products.SilvaDocument.silvaxml import xmlexport
    
    registerDirectory('widgets', globals())

    # new xml import/export
    xmlexport.initializeXMLExportRegistry()


# allow to access i18n from TTW code

from AccessControl import allow_module
allow_module('Products.SilvaDocument.i18n')



