## Script (Python) "set_simple_content"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=node, data
##title=
##
editorsupport = context.service_editorsupport
model = node.get_content()
# break data into seperate items
items = data.strip().split("\r\n\r\n")
# find containing child paragraph and replace data there
for child in node.childNodes:
    if child.nodeType == node.ELEMENT_NODE:
        break
    
supp = editorsupport.getMixedContentSupport(model, node)
supp.parse(items[0])

# if necessary, add new list items
if len(items) > 1:
    doc = node.ownerDocument
    next = node.nextSibling
    for item in items[1:]:
        li = doc.createElement('li')
        p = li.appendChild(doc.createElement('p'))
        #editorsupport.replace_text(p, item)
        supp = editorsupport.getMixedContentSupport(model, p)
        supp.parse(item)
        node.parentNode.insertBefore(li, next)
        
