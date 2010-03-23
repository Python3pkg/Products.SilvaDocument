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
from Products.SilvaDocument.i18n import translate as _

node = context.REQUEST.node
image = context.content()

if image is None:
    return '<div class="error">[' + unicode(_('image reference is broken')) + ']</div>'

alignment = node.getAttribute('alignment')

if not alignment:
    alignment = 'default'

tag_template = '%s'
if alignment.startswith('image-'):
    # I don't want to do this... Oh well, long live CSS..:
    # This style with the surrounding div makes the image
    # align left, center or right but not float.
    # Are there better ways? "display: block;" maybe?
    tag_template = '<div class="%s">%%s</div>' % alignment

params = {'class': alignment}
return tag_template % image.tag(**params)
