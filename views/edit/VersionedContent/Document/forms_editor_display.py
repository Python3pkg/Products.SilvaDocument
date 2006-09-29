## Script (Python) "get_tabs"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=active=None
##title=
##
from Products.SilvaDocument.i18n import translate as _

display = test(active, _('forms editor'), _('forms editor...'))
return display
