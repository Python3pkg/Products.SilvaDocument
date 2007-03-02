from zope.interface import implements
import Globals
from Products.Silva.adapters import adapter
from Products.Silva.adapters import interfaces

class DocumentFeedEntryAdapter(adapter.Adapter):
    """Adapter for Silva Documents to get an atom/rss feed entry 
    representation."""

    implements(interfaces.IFeedEntry)

    def __init__(self, context):
        self.context = context
        self.version = context.get_viewable()
        
    def id(self):
        return self.context.id
        
    def title(self):
        return "le titre"
    
    def description(self):
        return "testing<br /><strong>1, 2</strong>"
        
    def url(self):
        return "url"
        
    def authors(self):
        return ['a1', 'a2']
    
    def date_updated(self):
        return '2007-03-02T18:12:12ZCET'
    
    def date_published(self):
        return '2007-03-02T18:12:12ZCET'
    
    def keywords(self):
        return ['k1','k2']
