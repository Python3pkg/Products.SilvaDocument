# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from silva.core import conf as silvaconf
from Products.SilvaDocument import install

silvaconf.extensionName('SilvaDocument')
silvaconf.extensionTitle('Silva Document')
silvaconf.extensionDepends('SilvaExternalSources')



