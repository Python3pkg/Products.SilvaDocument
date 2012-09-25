# -*- coding: utf-8 -*-
# Copyright (c) 2011-2012 Infrae. All rights reserved.
# See also LICENSE.txt

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


# This layer is used to test the Silva upgrader to 3.0
class Silva30DocumentLayer(SilvaDocumentLayer):
    default_packages = SilvaLayer.default_packages + [
        'silva.app.document'
        ]

    def _install_application(self, app):
        super(Silva30DocumentLayer, self)._install_application(app)
        app.root.service_extensions.install('silva.app.document')
        transaction.commit()


FunctionalLayer = SilvaDocumentLayer(
    Products.SilvaDocument)
Functional30Layer = Silva30DocumentLayer(
    Products.SilvaDocument, zcml_file='ftesting30.zcml')
