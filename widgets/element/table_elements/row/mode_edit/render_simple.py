## Script (Python) "render_simple"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=node
##title=
##
model = node.get_content()
editorsupport = context.service_editorsupport

# find p first (FIXME: inefficient)
for child in node.childNodes:
  if child.nodeType == node.ELEMENT_NODE:
    break

node = child
supp = editorsupport.getMixedContentSupport(model, node)
text = supp.renderEditable()
text = editorsupport.replace_xml_entities(text)
return '''<textarea cols="20" rows="2" wrap="soft" class="fixIE6widget" 
    name="%s">%s</textarea>''' % (node.getNodePath('widget'), text)
