# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from silva.core.upgrade.upgrade import BaseUpgrader

import logging

logger = logging.getLogger('Products.SilvaDocument')

#-----------------------------------------------------------------------------
# 2.0.0 to 2.1.0
#-----------------------------------------------------------------------------

VERSION='2.1'

class DocumentUpgrader(BaseUpgrader):
    """Upgrade.
    """

    def upgrade(self, obj):
        obj._clean_cache()
        return obj


DocumentUpgrader = DocumentUpgrader(VERSION, 'Silva Document')

