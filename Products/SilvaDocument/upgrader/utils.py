# -*- coding: utf-8 -*-
# Copyright (c) 2011-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from urlparse import urlparse
import logging

from zExceptions import NotFound
from five.intid.site import aq_iter
from silva.core.interfaces import ISilvaObject



logger = logging.getLogger('Products.SilvaDocument')


def split_path(path, context, root=None):
    """Split path, remove . components, be sure there is enough parts
    in the context path to get all .. working.
    """
    if root is None:
        root = context.getPhysicalRoot()
    parts = path.split('/')
    if len(parts) and not parts[0]:
        context = root
    parts = filter(lambda x: x != '', parts)
    context_parts = filter(lambda x: x != '', list(context.getPhysicalPath()))
    root_parts = filter(lambda x: x != '', list(root.getPhysicalPath()))
    assert len(context_parts) >= len(root_parts)
    if len(root_parts):
        context_parts = context_parts[len(root_parts):]
    while parts:
        if parts[0] == '.':
            parts = parts[1:]
        elif parts[0] == '..':
            if len(context_parts):
                context_parts = context_parts[:-1]
                parts = parts[1:]
            else:
                raise KeyError(path)
        else:
            break
    return context_parts + parts, root


def resolve_path(url, content_path, context, obj_type=u'link'):
    """Resolve path to an object or report an error.
    """
    if isinstance(url, unicode):
        # If the link contains unicode, that is not a link.
        try:
            url.encode('ascii')
        except UnicodeEncodeError:
            logger.error(u"Invalid %s '%s' (contains unicode).", obj_type, url)
            return url, None, None
    url = url.strip()
    try:
        scheme, netloc, path, parameters, query, fragment = urlparse(url)
    except ValueError:
            logger.error(u"Invalid %s '%s' (is not a valid URL).", obj_type, url)
            return url, None, None
    if scheme:
        # This is a remote URL or invalid URL.
        #logger.debug(u'found a remote link %s' % url)
        return url, None, None
    if not path:
        # This is to an anchor in the document, nothing else
        return url, None, fragment
    try:
        cleaned_path, path_root = split_path(path, context)
        target = path_root.unrestrictedTraverse(cleaned_path)
    except (AttributeError, KeyError, NotFound, TypeError):
        # Try again using Silva Root as /
        try:
            cleaned_path, path_root = split_path(
                path, context, context.get_root())
            target = path_root.unrestrictedTraverse(cleaned_path)
        except (AttributeError, KeyError, NotFound, TypeError):
            logger.warn(
                u'Cannot resolve %s %s in %s',
                obj_type, url, content_path)
            return url, None, fragment
    if not ISilvaObject.providedBy(target):
        logger.error(
            u'%s %s did not resolve to a Silva content in %s',
            obj_type, path, content_path)
        return url, None, fragment
    try:
        [o for o in aq_iter(target, error=RuntimeError)]
        return url, target, fragment
    except RuntimeError:
        logger.error(
            u'Invalid target %s %s in %s',
            obj_type, path, content_path)
        return url, None, fragment
