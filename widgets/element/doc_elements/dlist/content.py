## Script (Python) "content"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
request = context.REQUEST
model = request.model
node = request.node
editorsupport = model.service_editorsupport
view_type = (context.id == 'mode_view') and 'public' or 'edit'

type = None
if node.hasAttribute('type'):
    type = node.getAttribute('type')

# first remove any crap
items = [child for child in node.childNodes if child.nodeType == node.ELEMENT_NODE and (child.nodeName == 'dt' or child.nodeName == 'dd')]

# now we're sure there are only dt's and dd's in the list. split them up into
# pairs
i = 0
pairs = []
while 1:
    if i >= len(items):
        break
    pair = []
    child = items[i]
    if child.nodeName == 'dt':
        supp = editorsupport.getMixedContentSupport(model, child)
        pair.append(supp.renderHTML(view_type=view_type))
        nextChild = items[i+1]
        if nextChild.nodeName == 'dd':
            supp = editorsupport.getMixedContentSupport(model, nextChild)
            pair.append(supp.renderHTML(view_type=view_type))
            pairs.append(pair)
            i += 1
        else:
            # should not happen, a dt without a following dd, but let's allow 
            # it anyway
            pair.append('')
    else:
        # as with the dt following a dt, a dd following a dd should not happen,
        # but let's allow it anyway
        supp = editorsupport.getMixedContentSupport(model, child)
        pair = ['', supp.renderHTML(view_type=view_type)]
    i += 1

return context.util.render_dlist(type, pairs)
