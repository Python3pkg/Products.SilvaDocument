from Products.Formulator.Errors import FormValidationError, ValidationError

request = context.REQUEST
node = request.node
session = request.SESSION

def removeParameterElements(node):
    removeChilds = [child for child in node.childNodes
                       if child.nodeType == node.ELEMENT_NODE
                           and child.nodeName == 'parameter']
    for child in removeChilds:
        try:
            node.removeChild(child)
        except ValueError:
            pass

def ustr(text, enc='utf-8'):
    if text is None:
        return u''
    elif same_type(text, ''):
        return unicode(text, enc, 'replace')
    elif same_type(text, u''):
        return text
    else:
        return unicode(str(text), enc, 'replace')

# save id and params if set
id = request.get('id')
if id is None:
    # no id nor params saved.
    removeParameterElements(node)
    node.removeAttribute('id')
    return

if node.getAttribute('id') != id:
    # is changed, so remove all attrs.
    node.setAttribute('id', ustr(id))

source = getattr(context, id, None)
if source is None:
    # should not happen since id was selected from a list...
    raise "Blerrrrrk!"

form = source.form()
try:
    result = form.validate_all_to_request(request)    
except (FormValidationError, ValidationError), errs:
    pass
else:
    removeParameterElements(node)
    for field in form.get_fields():
        param = node.createElement('parameter')
        param.setAttribute('key', ustr(field.id))
        node.appendChild(param)
        value = node.createTextNode(ustr(result[field.id]))
        param.appendChild(value)
