## Script (Python) "editable_content"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
node = context.REQUEST.node
render_field = context.render_editable_field

childnodes = [child for child in node.childNodes
              if child.nodeType == node.ELEMENT_NODE]

if not childnodes:
    return ''

countnodes = sum(
    [int(child.getAttribute('colspan') or 1) for child in childnodes])

texts = []
for child in childnodes:
    cellwidthperc = (
        int(child.getAttribute('colspan') or 1) * 1.0 / countnodes * 100)
    texts.append(render_field(node=child, cellwidth='%d%%' % (cellwidthperc,)))
return ''.join(texts)
