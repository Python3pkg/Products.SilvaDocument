# -*- coding: utf-8 -*-
# Copyright (c) 2012  Infrae. All rights reserved.
# See also LICENSE.txt
# XML Import/Export

from silva.core.xml import registerNamespace, registerOption

NS_DOCUMENT_URI = 'http://infrae.com/namespace/silva-document'
registerNamespace('doc', NS_DOCUMENT_URI)
registerOption('upgrade30', False)
registerOption('image_res', None)
