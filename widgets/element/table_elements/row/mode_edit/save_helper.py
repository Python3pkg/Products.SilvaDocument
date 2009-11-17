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

model = row.get_content()

# copy the fields into an array - this also allows inserting new fields in
# between the row's children while iterating through the fields
fields = [node for node in row.childNodes if node.nodeName == 'field']
skipnext = False
for i, field in enumerate(fields):
    if skipnext:
        continue
    fieldtype = request.get('rowFieldType_%s' % (i + 1,), 'td')
    field.setAttribute('fieldtype', fieldtype)
    merge = request.get('merge_%s' % (i + 1,))
    split = request.get('split_%s' % (i + 1,))
    if merge and not split:
        # merge
        next = field.nextSibling
        while next.nodeName != 'field':
            next = next.nextSibling
        while next.hasChildNodes():
            field.appendChild(next.firstChild)
        row.removeChild(next)
        field.setAttribute(
            'colspan', str(int(field.getAttribute('colspan') or 1) + 1))
        skipnext = True
    elif split and not merge:
        # create new field
        newfield = field.ownerDocument.createElement('field')
        newfield.setAttribute(
            'fieldtype', (field.getAttribute('fieldtype') or 'td'))
        newfield.appendChild(field.ownerDocument.createElement('p'))
        if field == row.lastChild:
            row.appendChild(newfield)
        else:
            row.insertBefore(newfield, field.nextSibling)
        field.setAttribute(
            'colspan', str(int(field.getAttribute('colspan')) - 1))

    if not context.is_field_simple(field):
        continue
    p_node = field.firstChild
    while (p_node and p_node.nodeName != 'p'):
        # basically this ignores text nodes.
        p_node = p_node.nextSibling
    if not p_node:
        raise ValueError, _("The stored xml is invalid.")
    data = request[p_node.getNodePath('widget')]
    supp = editorsupport.getMixedContentSupport(model, p_node)
    supp.parse(data)

