## Script (Python) "render_field"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=node, info
##title=
##
request = context.REQUEST
model = request.model

fieldType = node.getAttribute('fieldtype') or 'td'
colspan = node.getAttribute('colspan') or '1'
if colspan == '1':
    width = info.get('html_width') and ' width="%s"'%info.get('html_width') or ''
    colspan = ''
else:
    width = ''
    colspan = ' colspan="%s"'%colspan
middle = width+colspan
align = info['align']


if context.is_field_simple(node):
    # find p first (FIXME: inefficient)
    for child in node.childNodes:
        if child.nodeType == node.ELEMENT_NODE:
            break
    node = child
    if len(node.childNodes) == 0 or \
       (len(node.childNodes) == 1 and
        hasattr(node.childNodes[0].aq_explicit, 'data') and 
        len(node.childNodes[0].data.strip()) == 0):
        content ='&nbsp;'
    else:
        editorsupport = model.service_editorsupport
        supp = editorsupport.getMixedContentSupport(model, node)
        view_type = (context.id == 'mode_view') and 'public' or 'edit'
        content = supp.renderHTML(view_type=view_type)
else:
    context.service_editor.setViewer('service_sub_viewer')
    content = context.service_editor.renderView(node)
return '<%s class="align-%s"%s>%s</%s>' % (fieldType,
                                                    align,
                                                    middle,
                                                    content,
                                                    fieldType)

