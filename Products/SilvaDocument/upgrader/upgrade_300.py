# -*- coding: utf-8 -*-
# Copyright (c) 2011-2012 Infrae. All rights reserved.
# See also LICENSE.txt

import copy
import logging

from Acquisition import aq_parent, aq_base
from DateTime import DateTime
from OFS.CopySupport import CopyError
from zExceptions import BadRequest

from silva.core.interfaces import IPostUpgrader
from silva.core.interfaces import IVersionManager, IOrderManager
from silva.core.layout.interfaces import IMarkManager
from silva.core.references.interfaces import IReferenceService
from silva.core.services.interfaces import ICataloging
from silva.core.upgrade.upgrade import BaseUpgrader, content_path

from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility
from zope.interface import implements
from zope.publisher.browser import TestRequest

from Products.SilvaDocument.interfaces import IDocument
from Products.SilvaDocument.rendering.xsltrendererbase import XSLTTransformer
from Products.Silva.Membership import NoneMember

VERSION_A1='3.0a1'
logger = logging.getLogger('silva.core.upgrade')
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
    # Copy the old annotations to the version, it is possible we are
    # upgrading a 2.1 version that is not yet upgraded.
    old_annotations = getattr(aq_base(source), '_portal_annotations_', None)
    if old_annotations is not None:
        target._portal_annotations_ = old_annotations


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
    # Move text
    move_text(source, target)
    # Copy metadata content
    copy_annotation(source, target)
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
    user = aq_base(source.get_last_author_info())
    if not isinstance(user, NoneMember):
        target._last_author_userid = user.id
        target._last_author_info = aq_base(user)
    # Copy creator information
    target._owner = getattr(aq_base(source), '_owner', None)


class DocumentUpgrader(BaseUpgrader):
    """We convert a old SilvaDocument to a new one.
    """

    def validate(self, doc):
        return IDocument.providedBy(doc)

    def create_document(self, parent, identifier, title):
        factory = parent.manage_addProduct['silva.app.document']
        return factory.manage_addDocument(identifier, title)

    def copy_version(self, source, target, ensure=False):
        copy_version(source, target, ensure=ensure)

    def upgrade(self, doc):
        logger.info(u'Upgrading HTML in: %s.', content_path(doc))
        # ID + Title
        identifier = doc.id
        title = doc.get_title()
        parent = aq_parent(doc)

        # Create a new doccopy the annotation
        try:
            new_doc = self.create_document(
                parent, identifier + 'conv__silva30', title)
        except ValueError:
            logger.error(u'Cannot convert document: %s.', content_path(doc))
            return doc
        new_identifier = new_doc.getId() # The id can have changed
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

        # Markers
        new_mark_mg = IMarkManager(new_doc)
        for marker in IMarkManager(doc).usedMarkers:
            new_mark_mg.add_marker(marker)

        # Delete old document and rename content to final id
        order_mg = IOrderManager(parent)
        position = order_mg.get_position(doc)
        parent.manage_delObjects([identifier])
        try:
            parent.manage_renameObject(new_identifier, identifier)
        except CopyError:
            try:
                parent._checkId(identifier)
            except BadRequest:
                logger.error(
                    u"Could not replace document with '%s' identifier, renaming it to '%s_changed'.",
                    identifier, identifier)
                identifier += '_changed'
                parent.manage_renameObject(new_identifier, identifier)
            else:
                raise
        new_doc = parent[identifier]
        if position > -1:
            order_mg.move(new_doc, position)
        ICataloging(new_doc).reindex()
        return new_doc


document_upgrader = DocumentUpgrader(VERSION_A1, 'Obsolete Document')


class RootUpgrader(BaseUpgrader):

    def upgrade(self, root):
        # We need to install the new SilvaDocument, and Silva Obsolete
        # Document for the document migration.
        extensions = root.service_extensions
        if not extensions.is_installed('silva.app.document'):
            extensions.install('silva.app.document')
        if not extensions.is_installed('SilvaDocument'):
            extensions.install('SilvaDocument')
        return root

root_upgrader = RootUpgrader(VERSION_A1, 'Silva Root')


class RootPostUpgrader(BaseUpgrader):
    implements(IPostUpgrader)

    def upgrade(self, root):
        # We need to install the new SilvaDocument, and Silva Obsolete
        # Document for the document migration.
        extensions = root.service_extensions
        if extensions.is_installed('SilvaDocument'):
            extensions.uninstall('SilvaDocument')
        return root

root_post_upgrader = RootPostUpgrader(VERSION_A1, 'Silva Root')
