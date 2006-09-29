## Script (Python) "kupu_display"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=active=None
##title=
##
from Products.SilvaDocument.i18n import translate as _

display = test(active, _('kupu editor'), _('kupu editor...'))
return display
