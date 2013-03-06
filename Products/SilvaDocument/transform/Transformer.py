# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt
"""
Basic API for transforming Silva-XML to other formats.

currently only transformation to and from

    eopro2_11 (aka RealObjects EditOnPro)

is supported.

"""
__author__='Holger P. Krekel <hpk@trillke.net>'
__version__='$Revision: 1.4 $'

from Products.SilvaDocument.transform.ObjectParser import ObjectParser
from Products.SilvaDocument.transform.kupu import silvaformat, htmlformat

EDITORS = {'kupu': (silvaformat, htmlformat)}


class Transformer(object):
    """ Transform xml trees using pythonic xist-like
        specifications.
    """

    def __init__(self, source=silvaformat, target=htmlformat):
        """ provide a transformer from source to target
            (and possibly back).
        """
        self.source_parser = ObjectParser(source)
        self.target_parser = ObjectParser(target)

    def to_target(self, sourceobj, context, compacting=True):
        context.begin_transform()
        node = self.source_parser.parse(sourceobj)
        if compacting:
            node = node.compact()
        result = node.convert(context=context)
        context.finish_transform()
        return result

    def to_source(self, targetobj, context, compacting=True, cleaner=None):
        context.begin_transform()
        node = self.target_parser.parse(targetobj)
        if compacting:
            node = node.compact()
        result = node.convert(context=context)
        if cleaner is not None:
            cleaner(result)
        context.finish_transform()
        return result


class EditorTransformer(Transformer):
    """Transformer that transform differently depending the selected
    editor.
    """

    def __init__(self, editor='kupu'):
        if editor in EDITORS:
            super(EditorTransformer, self).__init__(
                source=EDITORS[editor][0],
                target=EDITORS[editor][1])
        else:
            raise ValueError("Unknown Editor: %s" % editor)
