## Script (Python) "get_title_text"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=node, html_encoded=None
##title=helper: get the rendered content of the <title> tag
##
request = context.REQUEST
model = request.model
editorsupport = context.service_editorsupport

for child in node.childNodes:
    if child.nodeName == 'title':
        supp = editorsupport.getMixedContentSupport(model, child)
        if html_encoded:
            view_type = (context.id == 'mode_view') and 'public' or 'edit'
            return supp.renderHTML(view_type=view_type)
        return supp.renderEditable()

return ''
