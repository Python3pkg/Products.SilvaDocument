# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from silva.core import conf as silvaconf

silvaconf.extensionName('SilvaDocument')
silvaconf.extensionTitle('Silva Document')
silvaconf.extensionDepends('SilvaExternalSources')


def initialize(context):
    from Products.SilvaDocument.silvaxml import xmlexport

    # new xml import/export
    xmlexport.initializeXMLExportRegistry()


