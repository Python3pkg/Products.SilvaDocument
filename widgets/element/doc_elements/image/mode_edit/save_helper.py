# $Id: save_helper.py,v 1.2 2003/09/02 14:28:46 jw Exp $
from Products.Silva.mangle import String

request = context.REQUEST
node = request.node

if request.has_key('alignment'):
    align_attribute = request['alignment']
    if align_attribute != 'none':
        node.setAttribute('alignment', String.inputConvert(align_attribute))
    else:
        node.removeAttribute('alignment')

if request.has_key('link'):
    link = request['link']
    node.setAttribute('link', String.inputConvert(link))
else:
    node.removeAttribute('link')

image_path = request['path']
node.setAttribute('path', String.inputConvert(image_path))
