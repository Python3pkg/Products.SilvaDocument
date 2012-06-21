# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import copy
import logging

from Acquisition import aq_parent, aq_base
from DateTime import DateTime

from silva.core.interfaces import IVersionManager, IOrderManager
from silva.core.references.interfaces import IReferenceService
from silva.core.upgrade.upgrade import BaseUpgrader, content_path
from silva.core.services.interfaces import ICataloging

from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility
from zope.publisher.browser import TestRequest

from Products.SilvaDocument.interfaces import IDocument
from Products.SilvaDocument.rendering.xsltrendererbase import XSLTTransformer
from Products.Silva.Membership import NoneMember

logger = logging.getLogger('silva.core.upgrade')


VERSION_A0='3.0a0'


UpgradeHTML = XSLTTransformer('upgrade_300.xslt', __file__)


def copy_annotation(source, target):
    """Copy Zope annotations from source to target.
    """
    # Metadata and subscriptions are stored as annotations. This
    # migrates them.
    source_anno = IAnnotations(source)
    target_anno = IAnnotations(target)
    for key in source_anno.keys():
        target_anno[key] = copy.deepcopy(source_anno[key])


def move_references(source, target):
    """Move references form source to target.
    """
    service = getUtility(IReferenceService)
    # list are here required. You cannot iterator and change the
    # result at the same time, as they won't appear in the result any
    # more and move eveything. :)
    for reference in list(service.get_references_to(source)):
        reference.set_target(target)
    for reference in list(service.get_references_from(source)):
        reference.set_source(target)


def move_text(source, target):
    """Move text content from old SilvaDocument source to a
    silva.app.document target.
    """
    request = TestRequest()
    html = UpgradeHTML.transform(source, request, options={'upgrade30': True})

    move_references(source, target)

    target.body.save(target, request, html)


def copy_version(source, target, ensure=False):
    """Copy version document from source to target.
    """
    # Copy metadata content
    copy_annotation(source, target)
    # Move text
    move_text(source, target)
    # Publication datetime
    info = IVersionManager(source)
    publication_datetime = info.get_publication_datetime()
    if publication_datetime is None and ensure:
        publication_datetime = DateTime()
    target.set_unapproved_version_publication_datetime(
        publication_datetime)
    target.set_unapproved_version_expiration_datetime(
        info.get_expiration_datetime())
    # Copy last author information
    user = aq_base(source.sec_get_last_author_info())
    if not isinstance(user, NoneMember):
        target._last_author_userid = user.id
        target._last_author_info = user
    # Copy creator information
    target._owner = getattr(aq_base(source), '_owner', None)


class DocumentUpgrader(BaseUpgrader):
    """We convert a old SilvaDocument to a new one.
    """

    def create_document(self, parent, identifier, title):
        factory = parent.manage_addProduct['silva.app.document']
        factory.manage_addDocument(identifier, title)

    def copy_version(self, source, target, ensure=False):
        copy_version(source, target, ensure=ensure)

    def upgrade(self, doc):
        if IDocument.providedBy(doc):
            logger.info(u'upgrading HTML content in: %s', content_path(doc))
            # ID + Title
            identifier = doc.id
            title = doc.get_title()
            parent = aq_parent(doc)

            # Create a new doccopy the annotation
            tmp_identifier = identifier + '__conv_silva30'
            self.create_document(parent, tmp_identifier, title)
            new_doc = parent[tmp_identifier]
            # Copy annotation
            copy_annotation(doc, new_doc)
            # Move references
            move_references(doc, new_doc)

            # Last closed version
            last_closed_version_id = doc.get_last_closed_version()
            if last_closed_version_id is not None:
                last_closed_version = doc._getOb(last_closed_version_id, None)
                if last_closed_version is not None:
                    new_last_closed_version = new_doc.get_editable()
                    self.copy_version(
                        last_closed_version, new_last_closed_version, True)
                    new_doc.approve_version()
                    if new_doc.get_public_version():
                        # The version can already be expired
                        new_doc.close_version()
                    new_doc.create_copy()

            # Published version
            public_version = doc.get_viewable()
            if public_version is not None:
                new_public_version = new_doc.get_editable()
                self.copy_version(
                    public_version, new_public_version, True)
                new_doc.approve_version()

            # Editable version
            editable_version = doc.get_editable()
            if editable_version is not None:
                if public_version is not None:
                    new_doc.create_copy()
                new_editable_version = new_doc.get_editable()
                self.copy_version(
                    editable_version, new_editable_version)

            # Delete old document and rename content to final id
            manager = IOrderManager(parent)
            position = manager.get_position(doc)
            parent.manage_delObjects([identifier])
            parent.manage_renameObject(tmp_identifier, identifier)
            new_doc = parent[identifier]
            manager.move(new_doc, position)
            ICataloging(new_doc).reindex()
            return new_doc
        return doc


document_upgrader = DocumentUpgrader(VERSION_A0, 'Obsolete Document')
