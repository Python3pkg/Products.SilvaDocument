
## Script (Python) "save_helper"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
from Products.SilvaDocument.i18n import translate as _

request = context.REQUEST
row = request.node
editorsupport = context.service_editorsupport
node = row.firstChild

fieldTypes = request.get('rowFieldType',[])
colspans = request.get('colspans',[])

model = node.get_content()

fieldNum = -1
while node is not None:
    field = node
    node = node.nextSibling
    if field.nodeName != 'field':
        continue
    fieldNum += 1
    if fieldNum + 1 <= len(fieldTypes):
        field.setAttribute('fieldtype',fieldTypes[fieldNum]=='th' and 'th' or 'td')
        try:
            cs = int(colspans[fieldNum])
        except:
            cs = 1
        field.setAttribute('colspan',str(cs))
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

