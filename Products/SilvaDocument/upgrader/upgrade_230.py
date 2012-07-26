# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import logging

from Products.SilvaDocument.upgrader.utils import resolve_path
from Products.SilvaDocument.interfaces import IDocument
from Products.SilvaDocument.transform.base import Context
from silva.core.upgrade.upgrade import BaseUpgrader, content_path


logger = logging.getLogger('Products.SilvaDocument')


#-----------------------------------------------------------------------------
# 2.2.0 to 2.3.0b1
#-----------------------------------------------------------------------------

VERSION_B1='2.3b1'


def build_reference(context, target, node):
    """Create a new reference to the given target and store it on the
    node.
    """
    reference_name, reference = context.new_reference()
    reference.set_target(target)
    node.setAttribute('reference', reference_name)


class DocumentUpgrader(BaseUpgrader):
    """We rewrite here document links and images in order to use
    references where ever it is possible.
    """

    def validate(self, doc):
        return IDocument.providedBy(doc)

    def upgrade(self, doc):
        # The 3.0 upgrader only upgrade the published, working and
        # last closed version. Only apply this upgrader on thoses.
        for version_id in [doc.get_public_version(),
                           doc.get_unapproved_version(),
                           doc.get_last_closed_version()]:
            if version_id is None:
                continue
            version = doc._getOb(version_id, None)
            if version is None or not hasattr(version, 'content'):
                continue
            dom = version.content.documentElement
            context = Context(version, None)
            self._upgrade_links(version, context, dom)
            self._upgrade_images(version, context, dom)
        return doc

    def _upgrade_links(self, version, context, dom):
        links = dom.getElementsByTagName('link')
        version_path = content_path(version)
        if links:
            logger.info(u'Upgrading links in: %s', version_path)
        for link in links:
            if link.hasAttribute('reference'):
                # Already migrated
                continue
            path = link.getAttribute('url')
            # Look for object
            url, target, fragment = resolve_path(
                path, version_path, context.model)
            if fragment:
                link.setAttribute('anchor', fragment)
                link.removeAttribute('url')
            if target is None:
                if not fragment:
                    link.setAttribute('url', url)
                continue
            build_reference(context, target, link)
            if not fragment:
                link.removeAttribute('url')

    def _upgrade_images(self, version, context, dom):
        images = dom.getElementsByTagName('image')
        version_path = content_path(version)

        def make_link(image, target, title='', window_target='', fragment=''):
            """Create a link, replace the image with it and set the
            image as child of the link.
            """
            link = dom.createElement('link')
            if not isinstance(target, basestring):
                build_reference(context, target, link)
            else:
                link.setAttribute('url', target)
            if fragment:
                link.setAttribute('anchor', fragment)
            if title:
                link.setAttribute('title', title)
            if window_target:
                link.setAttribute('target', window_target)
            parent = image.parentNode
            parent.replaceChild(link, image)
            link.appendChild(image)
            return link

        if images:
            logger.info('Upgrading images in: %s', version_path)
        for image in images:
            if image.hasAttribute('reference'):
                # Already a reference
                continue
            path = image.getAttribute('path')
            url, target, fragment = resolve_path(
                path, version_path, context.model, 'image')
            if target is not None:
                # If the image target is found it is changed to a
                # reference. However if it is not, we still want to
                # process the other aspect of the image tag migration
                # so just don't do continue here.
                build_reference(context, target, image)
                image.removeAttribute('path')
                image.removeAttribute('rewritten_path')
            # Collect link title/target
            title = ''
            if image.hasAttribute('title'):
                title = image.getAttribute('title')
                image.removeAttribute('title')
            window_target = ''
            if image.hasAttribute('target'):
                window_target = image.getAttribute('target')
                image.removeAttribute('target')
            link_set = False
            # Check for a link
            if image.hasAttribute('link'):
                link = image.getAttribute('link')
                if link:
                    link_url, link_target, fragment = resolve_path(
                        link, version_path, context.model)
                    if link_target is not None:
                        make_link(
                            image, link_target, title, window_target, fragment)
                    elif fragment:
                        make_link(image, '', title, window_target, fragment)
                    else:
                        make_link(image, link_url, title, window_target)
                    link_set = True
                image.removeAttribute('link')
            # Check for a link to high resolution version of the image
            if image.hasAttribute('link_to_hires'):
                link = image.getAttribute('link_to_hires')
                if link == '1' and link_set is False:
                    make_link(image, target, title, window_target)
                    link_set = True
                image.removeAttribute('link_to_hires')
            # Save the image title (aka alt) to its new name
            if image.hasAttribute('image_title'):
                title = image.getAttribute('image_title')
                image.removeAttribute('image_title')
                image.setAttribute('title', title)


document_upgrader = DocumentUpgrader(VERSION_B1, 'Obsolete Document')


