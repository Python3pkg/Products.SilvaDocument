"""
Basic API for transforming Silva-XML to other formats.

currently only transformation to and from

    eopro2_11 (aka RealObjects EditOnPro) 

is supported.

"""

__author__='Holger P. Krekel <hpk@trillke.net>'
__version__='$Revision: 1.4 $'

from Products.Silva.i18n import translate as _

class Transformer:
    """ Transform xml trees using pythonic xist-like
        specifications.  
    """
    from ObjectParser import ObjectParser

    def __init__(self, source='kupu.silva', target='kupu.html'):
        """ provide a transformer from source to target 
            (and possibly back).
        """
        self.source_spec = __import__(source, globals(), locals(), [], -1)
        self.target_spec = __import__(target, globals(), locals(), [], -1)
        self.source_parser = self.ObjectParser(self.source_spec)
        self.target_parser = self.ObjectParser(self.target_spec)

    def to_target(self, sourceobj, context=None, compacting=1):
        context = context or {}
        node = self.source_parser.parse(sourceobj)
        if compacting:
            node = node.compact()
        return node.convert(context=context)

    def to_source(self, targetobj, context=None, compacting=1, cleaner=None):
        context = context or {}
        node = self.target_parser.parse(targetobj)
        if compacting:
            node = node.compact()
        ret = node.convert(context=context)
        if cleaner is not None:
            cleaner(ret)
        return ret

class EditorTransformer(Transformer):
    def __init__(self, editor='kupu'):
        if editor == 'kupu':
            Transformer.__init__(self, 
                                 source='kupu.silva', 
                                 target='kupu.html')
        else:
            message = _("Unknown Editor: ${editor}",
                        mapping={'editor': editor})
            raise message
