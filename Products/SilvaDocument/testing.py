# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Products.Silva.testing import SilvaLayer
import Products.SilvaDocument
import transaction


class SilvaDocumentLayer(SilvaLayer):
    default_products = SilvaLayer.default_products + [
        'SilvaExternalSources',
        'SilvaDocument',
        ]

    def _install_application(self, app):
        super(SilvaDocumentLayer, self)._install_application(app)
        app.root.service_extensions.install('SilvaDocument')
        transaction.commit()


FunctionalLayer = SilvaDocumentLayer(Products.SilvaDocument)
