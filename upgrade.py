# zope imports
import zLOG

# silva imports
from Products.Silva.interfaces import IUpgrader
from Products.Silva import upgrade

from Products.SilvaDocument.Document import Document, DocumentVersion

class SwitchClass:
    
    __implements__ = IUpgrader

    def __init__(self, new_class, args=(), kwargs={}):
        self.new_class = new_class
        self.args = args
        self.kwargs = kwargs

    def upgrade(self, obj):
        obj_id = obj.getId()
        new_obj = self.new_class(obj_id, *self.args, **self.kwargs)
        new_obj.__dict__.update(obj.__dict__)
        container = obj.aq_parent
        setattr(container, obj_id, new_obj)
        new_obj = getattr(container, obj_id)
        return new_obj
   
    def __repr__(self):
        return "<SwitchClass %r>" % self.new_class

def initialize():
    upgrade.registry.registerUpgrader(SwitchClass(Document),
        '0.9.3', Document.meta_type)
    upgrade.registry.registerUpgrader(SwitchClass(DocumentVersion,
        args=('', )), '0.9.3', DocumentVersion.meta_type)

