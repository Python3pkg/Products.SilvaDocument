## Script (Python) "save_helper"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
from Products.Silva.i18n import translate as _

request = context.REQUEST
row = request.node
editorsupport = context.service_editorsupport
node = row.firstChild

model = node.get_content()

while node is not None:
    field = node
    node = node.nextSibling
    if field.nodeName != 'field':
        continue
    if not context.is_field_simple(field):
        continue
    p_node = field.firstChild
    while (p_node and p_node.nodeName != 'p'):
        # basictly this ignores text nodes.
        p_node = p_node.nextSibling
    if not p_node:
        raise ValueError, _("The stored xml is invalid.")
    data = request[p_node.getNodePath('widget')]
    supp = editorsupport.getMixedContentSupport(model, p_node)
    supp.parse(data)
