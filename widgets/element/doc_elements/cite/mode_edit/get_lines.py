## Script (Python) "get_lines"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
text = context.editable('p')
l = len(text) / 40
if l < 12:
    return 12
else:
    return l
