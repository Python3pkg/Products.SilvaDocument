## Script (Python) "get_image"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=image_context, image_path
##title=
##
image = image_context.restrictedTraverse(image_path, None)
if image is None:
    return None

if getattr(image, 'meta_type', None) != 'Silva Image':
    image = None
    
return image

