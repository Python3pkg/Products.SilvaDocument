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

if context.is_field_simple(node):
    # find p first (FIXME: inefficient)
    for child in node.childNodes:
        if child.nodeType == node.ELEMENT_NODE:
            break
    node = child
    if len(node.childNodes) == 0:
        return '<td class="align-%s" width="%s">&nbsp;</td>' % (info['align'], 
            info['html_width'])
    if (len(node.childNodes) == 1 and hasattr(node.childNodes[0], 'data') and 
            len(node.childNodes[0].data.strip()) == 0):
        return '<td class="align-%s" width="%s">&nbsp;</td>' % (info['align'], 
            info['html_width'])
    else:
        editorsupport = model.service_editorsupport
        supp = editorsupport.getMixedContentSupport(model, node)
        view_type = (context.id == 'mode_view') and 'public' or 'edit'
        return '<td class="align-%s" width="%s">%s</td>' % (
            info['align'], info['html_width'], 
            supp.renderHTML(view_type=view_type))
else:
    context.service_editor.setViewer('service_sub_previewer')
    content = context.service_editor.renderView(node)
    return '<td class="align-%s" width="%s">%s</td>' % (info['align'],
        info['html_width'], content)
