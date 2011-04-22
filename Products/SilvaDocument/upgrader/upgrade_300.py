# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import copy
import logging

from Acquisition import aq_parent

from silva.core.interfaces import IVersionManager
from silva.core.editor.transform.interfaces import ISaveEditorFilter
from silva.core.editor.transform.interfaces import ITransformer
from silva.core.references.interfaces import IReferenceService
from silva.core.upgrade.upgrade import BaseUpgrader, content_path
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility, getMultiAdapter
from zope.publisher.browser import TestRequest

from Products.SilvaDocument.interfaces import IDocument
from Products.SilvaDocument.rendering.xsltrendererbase import XSLTTransformer

logger = logging.getLogger('silva.core.upgrade')


VERSION_A0='3.0a0'


DocumentHTML = XSLTTransformer('document.xslt', __file__)


def copy_annotation(source, target):
    source_anno = IAnnotations(source)
    target_anno = IAnnotations(target)
    for key in source_anno.keys():
        target_anno[key] = copy.deepcopy(source_anno[key])


def move_references(source, target):
    service = getUtility(IReferenceService)
    for reference in service.get_references_to(source):
        reference.set_target(target)


def move_text(source, target):
    request = TestRequest()
    html = DocumentHTML.transform(source, request, options={'upgrade30': True})
    transformer = getMultiAdapter((target, request), ITransformer)
    target.body.save_raw_text(transformer.data(
            'body', target.body, html, ISaveEditorFilter))


class DocumentUpgrader(BaseUpgrader):
    """We convert a old SilvaDocument to a new one.
    """

    def upgrade(self, doc):
        if IDocument.providedBy(doc):
            logger.info(u'upgrading document in: %s', content_path(doc))
            # ID + Title
            identifier = doc.id
            title = doc.get_title()
            parent = aq_parent(doc)

            # Create a new doccopy the annotation
            tmp_identifier = identifier + '__conv_silva30'
            factory = parent.manage_addProduct['silva.app.document']
            factory.manage_addDocument(tmp_identifier, title)
            new_doc = parent[tmp_identifier]
            # Copy annotation
            copy_annotation(doc, new_doc)
            # Move references
            move_references(doc, new_doc)

            # Published version
            public_version = doc.get_viewable()
            if public_version is not None:
                new_public_version = new_doc.get_editable()
                # Copy metadata content
                copy_annotation(public_version, new_public_version)
                # Move references
                move_references(public_version, new_public_version)
                # Move text
                move_text(public_version, new_public_version)
                # Publication datetime
                info = IVersionManager(public_version)
                new_public_version.set_unapproved_version_publication_datetime(
                    info.get_publication_datetime())
                new_public_version.set_unapproved_version_expiration_datetime(
                    info.get_expiration_datetime())
                new_public_version.approve_version()

            # Editable version
            editable_version = doc.get_editable()
            if editable_version is not None:
                if public_version is not None:
                    new_doc.create_copy()
                new_editable_version = new_doc.get_editable()
                # Copy metadata content
                copy_annotation(editable_version, new_editable_version)
                # Move references
                move_references(editable_version, new_editable_version)
                # Move text
                move_text(editable_version, new_editable_version)
                # Publication datetime
                info = IVersionManager(public_version)
                new_editable_version.set_unapproved_version_publication_datetime(
                    info.get_publication_datetime())
                new_editable_version.set_unapproved_version_expiration_datetime(
                    info.get_expiration_datetime())

            # Delete old document and rename content to final id
            parent.manage_delObjects([identifier])
            parent.manage_renameObject(tmp_identifier, identifier)
            return parent[identifier]
        return doc


document_upgrader = DocumentUpgrader(VERSION_A0, 'Silva Document')
