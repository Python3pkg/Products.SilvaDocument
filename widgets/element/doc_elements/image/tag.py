## Script (Python) "tag"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

from Products.Silva.mangle import entities
from Products.Silva.i18n import translate as _

node = context.REQUEST.node
image = context.content()

if not image:
    return _('<div class="error">[image reference is broken]</div>')

alignment = node.getAttribute('alignment')
link = node.getAttribute('link')
link_title = node.getAttribute('title')
target = node.getAttribute('target')

if not alignment:
    alignment = 'default'

if not link_title:
    link_title = image.get_title()

tag_template = '%s'
if alignment.startswith('image-'):
    # I don't want to do this... Oh well, long live CSS..:
    # This style with the surrounding div makes the image
    # align left, center or right but not float.
    # Are there better ways? "display: block;" maybe?
    tag_template = '<div class="%s">%%s</div>' % alignment

params = {
    'class': alignment, 'title': link_title
    }    
tag = tag_template % image.tag(**params)

if link:
    tag = '<a class="image" href="%s" title="%s" target="%s">%s</a>' % (
        entities(link), link_title, target, tag)

return tag
