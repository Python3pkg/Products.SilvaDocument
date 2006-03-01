from Products.Five import BrowserView

class EmptyNotes(BrowserView):
    
    def __call__(self):
        return ''
