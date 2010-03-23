## Script (Python) "content"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
node = context.REQUEST.node
model = context.REQUEST.model
image_path = node.getAttribute('path').encode('ascii', 'ignore')
if not image_path:
    reference_name = node.getAttribute('reference').encode('ascii', 'ignore')
    reference = model.service_references.get_reference(model, reference_name)
    if reference is None:
        return None
    return reference.target
return context.get_image(node.get_container(), image_path)
