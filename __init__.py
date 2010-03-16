# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from AccessControl import allow_module
from Products.FileSystemSite.DirectoryView import registerDirectory
from silva.core import conf as silvaconf

silvaconf.extensionName('SilvaDocument')
silvaconf.extensionTitle('Silva Document')
silvaconf.extensionDepends('SilvaExternalSources')

def initialize(context):
    from Products.SilvaDocument.silvaxml import xmlexport

    registerDirectory('widgets', globals())

    # new xml import/export
    xmlexport.initializeXMLExportRegistry()


# allow to access i18n from TTW code
allow_module('Products.SilvaDocument.i18n')

