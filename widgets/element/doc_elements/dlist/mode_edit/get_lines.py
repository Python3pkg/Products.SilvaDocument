## Script (Python) "get_lines"
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
editorsupport = context.service_editorsupport

l = 0
for child in node.childNodes:
    if child.nodeType != node.ELEMENT_NODE:
        continue
    if child.nodeName == 'dt' or child.nodeType == 'dd':
        supp = editorsupport.getMixedContentSupport(model, child)
        text = supp.renderEditable()
        t = len(text) / 40
        if t == 0:
            t = 1
        l += t
    if child.nodeName == 'dd':
        # add an extra line, since <dd>'s will be split with a double newline
        l += 1
    l += 1
if l < 7:
    return 7
else:
    return l
