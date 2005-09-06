## Script (Python) "content"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
from Products.SilvaDocument.i18n import translate as _

code = context.get_code_object()

if not code:
    return '<span class="warning">[' + unicode(_('Code element is broken')) + ']</span>'

# this is also done in get_code(), but I need to get to path:
node = context.REQUEST.node
path = node.getAttribute('path')

message = _('Code element: ${title_or_id} at ${path}')
message.set_mapping({'title_or_id': code.title_or_id(), 'path': path})

return  message

